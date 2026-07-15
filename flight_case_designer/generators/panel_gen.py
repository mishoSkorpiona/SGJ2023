# SPDX-License-Identifier: GPL-3.0-or-later
"""
Panel generator – creates the six plywood panels for the body and lid.

Panel layout (standard butt-joint construction)
------------------------------------------------
* Top and bottom panels span the full external width × depth.
* Front and back panels fit between top and bottom, span full external width.
* Left and right (side) panels fill the remaining interior space.

For split cases (lift-off lid, hinged lid …) the panels are divided at
``dims.split_z`` into a **body** set and a **lid** set.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

from .mesh_utils import (
    create_flat_panel,
    get_or_create_material,
    link_object,
)

if TYPE_CHECKING:
    from .case_builder import CaseDimensions
    from ..properties import FCD_CaseProperties


# ---------------------------------------------------------------------------
# Material colours per material type
# ---------------------------------------------------------------------------

_PLY_COLORS = {
    "BIRCH":          (0.65, 0.55, 0.35, 1.0),
    "PHENOLIC_BIRCH": (0.10, 0.10, 0.10, 1.0),
    "MDF":            (0.70, 0.60, 0.50, 1.0),
}


def generate_panels(
    context:   bpy.types.Context,
    dims:      "CaseDimensions",
    case_props: "FCD_CaseProperties",
    body_col:  bpy.types.Collection,
    lid_col:   bpy.types.Collection,
) -> None:
    """
    Create all plywood panel objects and link them into *body_col* / *lid_col*.

    Parameters
    ----------
    dims:       Pre-computed case dimensions.
    case_props: Case property group (for material type, case type …).
    body_col:   Collection that receives body panels.
    lid_col:    Collection that receives lid panels.
    """
    color = _PLY_COLORS.get(case_props.material_type, (0.65, 0.55, 0.35, 1.0))
    mat   = get_or_create_material("FCD_Plywood", base_color=color, roughness=0.85)

    w   = dims.ext_w
    d   = dims.ext_d
    h   = dims.ext_h
    t   = dims.ply_t
    bh  = dims.body_h   # body height
    lh  = dims.lid_h    # lid  height
    sz  = dims.split_z  # seam Z

    has_lid = case_props.case_type not in ("CUSTOM_BOX",)

    # ------------------------------------------------------------------
    # Shared helper
    # ------------------------------------------------------------------

    def _make(name, width, depth, thickness, location, collection):
        obj = create_flat_panel(name, width, depth, thickness, location, material=mat)
        link_object(obj, collection)
        return obj

    # ------------------------------------------------------------------
    # Top and bottom panels  (full external W × D)
    # ------------------------------------------------------------------

    # Bottom panel
    _make("Panel_Bottom", w, d, t, (0, 0, 0), body_col)

    if has_lid:
        # Top panel belongs to the lid
        _make("Panel_Top", w, d, t, (0, 0, h - t), lid_col)
    else:
        _make("Panel_Top", w, d, t, (0, 0, h - t), body_col)

    # ------------------------------------------------------------------
    # Front and back panels  (full W, height = H − 2t)
    # Side panels are inset by front/back thickness (standard butt joints)
    # ------------------------------------------------------------------

    # Body front / back
    body_fb_h = bh - t          # from top of bottom panel to seam
    lid_fb_h  = lh - t          # from seam to bottom of top panel

    if has_lid:
        # --- Body ---
        _make("Panel_Body_Front", w, t, body_fb_h, (0,     0,       t), body_col)
        _make("Panel_Body_Back",  w, t, body_fb_h, (0, d - t,       t), body_col)

        side_w = d - 2 * t       # side panel depth (between front & back)
        _make("Panel_Body_Left",  t, side_w, body_fb_h, (0,   t, t), body_col)
        _make("Panel_Body_Right", t, side_w, body_fb_h, (w-t, t, t), body_col)

        # --- Lid ---
        _make("Panel_Lid_Front", w, t, lid_fb_h, (0,     0,  sz),     lid_col)
        _make("Panel_Lid_Back",  w, t, lid_fb_h, (0, d - t,  sz),     lid_col)
        _make("Panel_Lid_Left",  t, side_w, lid_fb_h, (0,   t, sz),   lid_col)
        _make("Panel_Lid_Right", t, side_w, lid_fb_h, (w-t, t, sz),   lid_col)

    else:
        # Single-piece box (CUSTOM_BOX) – no lid split
        fb_h = h - 2 * t
        side_w = d - 2 * t
        _make("Panel_Front", w, t, fb_h, (0,     0, t),   body_col)
        _make("Panel_Back",  w, t, fb_h, (0, d - t, t),   body_col)
        _make("Panel_Left",  t, side_w, fb_h, (0,   t, t), body_col)
        _make("Panel_Right", t, side_w, fb_h, (w-t, t, t), body_col)

    # ------------------------------------------------------------------
    # Rack case: add rack-rail support panels / cross-braces
    # ------------------------------------------------------------------
    if case_props.case_type == "RACK_CASE":
        _add_rack_panels(context, dims, mat, body_col)


def _add_rack_panels(
    context:  bpy.types.Context,
    dims:     "CaseDimensions",
    mat:      bpy.types.Material,
    body_col: bpy.types.Collection,
) -> None:
    """Add inner support ledges for rack rails."""
    w   = dims.ext_w
    d   = dims.ext_d
    t   = dims.ply_t
    bh  = dims.body_h
    # Rack-rail support shelf on each side – thin horizontal panel
    shelf_d = t * 2.0
    shelf_h = dims.int_h
    shelf_obj = create_flat_panel(
        "Rack_Support_Left", t, shelf_d, shelf_h,
        location=(t, t, t), material=mat
    )
    link_object(shelf_obj, body_col)
    shelf_r = create_flat_panel(
        "Rack_Support_Right", t, shelf_d, shelf_h,
        location=(w - 2 * t, t, t), material=mat
    )
    link_object(shelf_r, body_col)
