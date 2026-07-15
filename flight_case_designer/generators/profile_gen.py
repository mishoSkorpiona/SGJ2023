# SPDX-License-Identifier: GPL-3.0-or-later
"""
Aluminium profile generator.

Profiles are placed along all 12 external edges of the case box plus the four
edges of the body/lid seam.  The cross-section is determined by the profile
type selected in the UI.

Profiles run along the length of each edge; the cross-section sits on the
*outside* face of the plywood panel.  For simplicity the extrusion is
represented as a solid box whose width × height match the profile flange size
and whose depth equals the edge length.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

import bpy
from mathutils import Vector

from .mesh_utils import (
    create_box_mesh,
    extrude_profile_along_path,
    get_or_create_material,
    link_object,
)

if TYPE_CHECKING:
    from .case_builder import CaseDimensions
    from ..properties import FCD_CaseProperties

# ---------------------------------------------------------------------------
# Cross-section shapes (2-D outline in local XY, extruded along Z)
# Each returns a list of (x, y) tuples forming the closed polygon.
# ---------------------------------------------------------------------------

def _section_angle(size: float, thickness: float = 0.003) -> List[Tuple[float, float]]:
    """L-shaped angle profile."""
    s, t = size, thickness
    return [(0, 0), (s, 0), (s, t), (t, t), (t, s), (0, s)]


def _section_double_angle(size: float, thickness: float = 0.003) -> List[Tuple[float, float]]:
    """T / double-angle profile."""
    s, t = size, thickness
    half = s / 2.0
    return [
        (0, 0), (s, 0), (s, t),
        (half + t / 2, t), (half + t / 2, s), (half - t / 2, s),
        (half - t / 2, t), (0, t),
    ]


def _section_h_profile(size: float, thickness: float = 0.003) -> List[Tuple[float, float]]:
    """H-section profile."""
    s, t = size, thickness
    mid = s / 2.0
    return [
        (0, 0), (s, 0), (s, t), (mid + t / 2, t),
        (mid + t / 2, s - t), (s, s - t), (s, s), (0, s),
        (0, s - t), (mid - t / 2, s - t), (mid - t / 2, t), (0, t),
    ]


def _get_section(profile_type: str, size: float) -> List[Tuple[float, float]]:
    """Return 2-D cross-section verts for the given profile type."""
    funcs = {
        "ANGLE":         _section_angle,
        "DOUBLE_ANGLE":  _section_double_angle,
        "TONGUE_GROOVE": _section_angle,      # simplified
        "LID_PROFILE":   _section_angle,      # simplified
        "H_PROFILE":     _section_h_profile,
        "CORNER_PROFILE":_section_angle,      # simplified
    }
    fn = funcs.get(profile_type, _section_angle)
    return fn(size)


# ---------------------------------------------------------------------------
# Edge definitions – 12 box edges + 4 seam edges
# ---------------------------------------------------------------------------

def _box_edges(
    w: float, d: float, h: float, t: float
) -> List[Tuple[Vector, Vector, str]]:
    """
    Return (start, end, axis_hint) for all 12 external edges of a box.

    ``t`` is an inset so corner profiles do not overlap with corner hardware.
    """
    # Bottom loop (z = 0)
    b_fl = Vector((t,     t,     0))
    b_fr = Vector((w - t, t,     0))
    b_br = Vector((w - t, d - t, 0))
    b_bl = Vector((t,     d - t, 0))
    # Top loop (z = h)
    t_fl = Vector((t,     t,     h))
    t_fr = Vector((w - t, t,     h))
    t_br = Vector((w - t, d - t, h))
    t_bl = Vector((t,     d - t, h))

    return [
        # Bottom four edges
        (b_fl, b_fr, "bottom_front"),
        (b_fr, b_br, "bottom_right"),
        (b_br, b_bl, "bottom_back"),
        (b_bl, b_fl, "bottom_left"),
        # Top four edges
        (t_fl, t_fr, "top_front"),
        (t_fr, t_br, "top_right"),
        (t_br, t_bl, "top_back"),
        (t_bl, t_fl, "top_left"),
        # Four vertical edges
        (b_fl, t_fl, "vert_fl"),
        (b_fr, t_fr, "vert_fr"),
        (b_br, t_br, "vert_br"),
        (b_bl, t_bl, "vert_bl"),
    ]


def _seam_edges(
    w: float, d: float, sz: float, t: float
) -> List[Tuple[Vector, Vector, str]]:
    """Four horizontal seam edges at the body / lid interface."""
    return [
        (Vector((t, t,     sz)), Vector((w - t, t,     sz)), "seam_front"),
        (Vector((w - t, t, sz)), Vector((w - t, d - t, sz)), "seam_right"),
        (Vector((w - t, d - t, sz)), Vector((t, d - t, sz)), "seam_back"),
        (Vector((t, d - t, sz)), Vector((t, t, sz)),         "seam_left"),
    ]


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def generate_profiles(
    context:      bpy.types.Context,
    dims:         "CaseDimensions",
    case_props:   "FCD_CaseProperties",
    profiles_col: bpy.types.Collection,
) -> None:
    """
    Generate all aluminium extrusion objects and link them into *profiles_col*.
    """
    mat = get_or_create_material(
        "FCD_Aluminium",
        base_color=(0.75, 0.75, 0.80, 1.0),
        metallic=0.9,
        roughness=0.3,
    )

    w, d, h = dims.ext_w, dims.ext_d, dims.ext_h
    sz      = dims.split_z
    t       = dims.prof_t   # profile size in metres
    t_inset = t             # corner inset

    section = _get_section(case_props.profile_type, t)

    edges: List[Tuple[Vector, Vector, str]] = []

    # Full-height box edges
    full_h_edges = _box_edges(w, d, h, t_inset)

    # For split cases split the vertical edges at the seam
    has_seam = case_props.case_type not in ("CUSTOM_BOX",)

    for start, end, label in full_h_edges:
        if has_seam and "vert_" in label:
            # Split vertical edge at seam
            mid_z = sz
            mid_start = Vector((start.x, start.y, mid_z))
            mid_end   = Vector((end.x,   end.y,   mid_z))
            edges.append((start,     mid_start, label + "_body"))
            edges.append((mid_end,   end,       label + "_lid"))
        else:
            edges.append((start, end, label))

    # Seam edges
    if has_seam:
        edges.extend(_seam_edges(w, d, sz, t_inset))

    # Create one object per edge
    for i, (start, end, label) in enumerate(edges):
        name = f"Profile_{label}"
        obj  = extrude_profile_along_path(name, section, start, end, material=mat)
        if obj is None:
            continue
        link_object(obj, profiles_col)
