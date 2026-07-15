# SPDX-License-Identifier: GPL-3.0-or-later
"""
Foam generator.

Creates two foam blocks (base and lid) sized to fill the internal cavity.
An equipment cutout is carved using a Boolean modifier (DIFFERENCE) so that
the equipment sits perfectly in the foam.

Cutout styles
-------------
NONE         : Solid foam, no cutout.
SIMPLE       : Rectangular cutout matching equipment W × D, full foam depth.
OFFSET       : Inset cutout – 3 mm border left around the equipment outline.
FINGER_PULL  : Simple cutout with two semicircular grooves on the long sides.
MULTI_LAYER  : Two-layer foam (base layer + top pick-and-pluck layer).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import bmesh
from mathutils import Vector

from .mesh_utils import (
    create_box_mesh,
    create_cylinder,
    get_or_create_material,
    link_object,
)

if TYPE_CHECKING:
    from .case_builder import CaseDimensions
    from ..properties import FCD_EquipmentProperties, FCD_CaseProperties, FCD_FoamProperties


# ---------------------------------------------------------------------------
# Material colours per foam type
# ---------------------------------------------------------------------------

_FOAM_COLORS = {
    "EVA": (0.1, 0.1, 0.15, 0.85),
    "PE":  (0.15, 0.15, 0.2, 0.85),
    "PU":  (0.25, 0.1, 0.05, 0.85),
}


# ---------------------------------------------------------------------------
# Boolean cutout helper
# ---------------------------------------------------------------------------

def _apply_bool_cutout(
    base_obj: bpy.types.Object,
    cutter:   bpy.types.Object,
) -> None:
    """Apply a DIFFERENCE boolean modifier to *base_obj* using *cutter*."""
    mod = base_obj.modifiers.new("FCD_Bool_Cutout", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object    = cutter
    mod.solver    = "FAST"
    # Cutter should not be visible
    cutter.hide_render   = True
    cutter.hide_viewport = True


# ---------------------------------------------------------------------------
# Finger-pull groove creator
# ---------------------------------------------------------------------------

def _add_finger_pull_grooves(
    base_obj: bpy.types.Object,
    dims:     "CaseDimensions",
    foam_props: "FCD_FoamProperties",
    side: str,
) -> None:
    """
    Create two semicircular groove cutters on the long sides of *base_obj*.

    *side* is ``"base"`` or ``"lid"``.
    """
    from .mesh_utils import create_cylinder
    fp_depth = foam_props.finger_pull_depth / 1000.0
    fp_width = foam_props.finger_pull_width / 1000.0
    radius   = fp_width / 2.0

    eq_w = dims.eq_w
    eq_d = dims.eq_d
    cx   = dims.ply_t + dims.foam_l + eq_w / 2.0
    cy_l = dims.ply_t + dims.foam_f
    cy_r = dims.ply_t + dims.foam_f + eq_d

    for idx, cy in enumerate([cy_l, cy_r]):
        groove = create_cylinder(
            f"FingPull_{side}_{idx}", radius, fp_depth * 2,
            segments=16,
            location=(cx - radius, cy - fp_depth, 0.0),
        )
        _apply_bool_cutout(base_obj, groove)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_foam(
    context:     bpy.types.Context,
    dims:        "CaseDimensions",
    equip_props: "FCD_EquipmentProperties",
    case_props:  "FCD_CaseProperties",
    foam_props:  "FCD_FoamProperties",
    foam_col:    bpy.types.Collection,
) -> None:
    """Create foam block objects and link them into *foam_col*."""

    ftype  = foam_props.foam_type
    color  = _FOAM_COLORS.get(ftype, (0.1, 0.1, 0.15, 0.85))
    mat    = get_or_create_material(
        f"FCD_Foam_{ftype}", base_color=color, roughness=0.95, alpha=color[3]
    )

    t    = dims.ply_t
    w    = dims.int_w
    d    = dims.int_d
    bh   = dims.foam_b   # base foam block height
    th   = dims.foam_t   # lid  foam block height
    has_lid = case_props.case_type not in ("CUSTOM_BOX",)

    style = foam_props.cutout_style

    # ------------------------------------------------------------------ #
    # Base foam block
    # ------------------------------------------------------------------ #
    base_foam = create_box_mesh(
        "Foam_Base", w, d, bh,
        location=(t, t, t), material=mat
    )
    link_object(base_foam, foam_col)

    if style != "NONE":
        _carve_base_foam(base_foam, dims, foam_props)

    # ------------------------------------------------------------------ #
    # Lid foam block
    # ------------------------------------------------------------------ #
    if has_lid and th > 0.001:
        lid_foam_z = dims.ext_h - t - th
        lid_foam = create_box_mesh(
            "Foam_Lid", w, d, th,
            location=(t, t, lid_foam_z), material=mat
        )
        link_object(lid_foam, foam_col)

    # ------------------------------------------------------------------ #
    # Multi-layer: add a pick-and-pluck top layer
    # ------------------------------------------------------------------ #
    if style == "MULTI_LAYER":
        layer2_h = min(0.020, bh * 0.4)  # 20 mm or 40 % of base foam
        layer2_mat = get_or_create_material(
            "FCD_Foam_Layer2", base_color=(0.3, 0.3, 0.35, 0.7),
            roughness=0.95, alpha=0.7
        )
        layer2 = create_box_mesh(
            "Foam_PickPluck", w, d, layer2_h,
            location=(t, t, t + bh - layer2_h), material=layer2_mat
        )
        link_object(layer2, foam_col)


def _carve_base_foam(
    base_obj: bpy.types.Object,
    dims:     "CaseDimensions",
    foam_props: "FCD_FoamProperties",
) -> None:
    """Apply the appropriate cutout to the base foam block."""
    style  = foam_props.cutout_style
    offset = 0.003 if style == "OFFSET" else 0.0  # 3 mm inset for OFFSET style

    eq_w = dims.eq_w - 2 * offset
    eq_d = dims.eq_d - 2 * offset
    eq_h = dims.eq_h  # full cutout depth

    cx = dims.foam_l + offset
    cy = dims.foam_f + offset
    cz = 0.0   # starts at base of foam block (will be cut from top)

    # Position the cutter inside the foam block coordinate space
    cutter = create_box_mesh(
        "FCD_Cutter_Base", eq_w, eq_d, eq_h * 2.0,
        location=(
            dims.ply_t + cx,
            dims.ply_t + cy,
            dims.ply_t + dims.foam_b - eq_h,
        ),
    )

    _apply_bool_cutout(base_obj, cutter)

    if style == "FINGER_PULL":
        _add_finger_pull_grooves(base_obj, dims, foam_props, "base")
