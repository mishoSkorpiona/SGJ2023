# SPDX-License-Identifier: GPL-3.0-or-later
"""
Hardware placement generator.

Reads the ``FCD_HardwareProperties`` group and the case dimensions, then uses
the hardware catalog from ``libraries.hardware_data`` to generate proxy mesh
objects at each computed position.

Auto-placement rules
--------------------
* **Latches** – centred on the front face at the body/lid seam, spaced evenly.
  Count is auto-determined from case width if ``latch_count == 0``.
* **Handles** – centred on each side panel, count from weight rule.
* **Corners** – one per corner of the case (8 total for body + lid).
* **Feet / Casters** – four at the bottom corners.
* **Hinges** – rear face at seam (hinged-lid cases only).
* **Stacking cups** – top face corners.
* **Label holder** – front face, body lower half.
* **Rack rails** – inner front edges (rack-case only).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple

import bpy
from mathutils import Vector

from .mesh_utils import (
    create_box_mesh,
    create_cylinder,
    get_or_create_material,
    link_object,
)

if TYPE_CHECKING:
    from .case_builder import CaseDimensions
    from ..properties import FCD_EquipmentProperties, FCD_CaseProperties, FCD_HardwareProperties


# ---------------------------------------------------------------------------
# Proxy-mesh helpers
# ---------------------------------------------------------------------------

def _hw_box(name, w, d, h, loc, mat):
    obj = create_box_mesh(name, w, d, h, location=loc, material=mat)
    return obj

def _hw_cyl(name, radius, depth, loc, mat):
    obj = create_cylinder(name, radius, depth, segments=16, location=loc, material=mat)
    return obj


# ---------------------------------------------------------------------------
# Placement helpers
# ---------------------------------------------------------------------------

def _even_positions(total_length: float, count: int, item_width: float) -> List[float]:
    """
    Return *count* X offsets that space items evenly across *total_length*.
    """
    if count == 1:
        return [total_length / 2.0 - item_width / 2.0]
    spacing = (total_length - item_width) / (count - 1)
    return [i * spacing for i in range(count)]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_hardware(
    context:    bpy.types.Context,
    dims:       "CaseDimensions",
    equip_props: "FCD_EquipmentProperties",
    case_props:  "FCD_CaseProperties",
    hdw_props:   "FCD_HardwareProperties",
    hw_col:     bpy.types.Collection,
) -> None:
    """Create all hardware proxy objects and link them into *hw_col*."""

    mat_chrome = get_or_create_material(
        "FCD_Chrome", base_color=(0.9, 0.9, 0.92, 1.0), metallic=1.0, roughness=0.15
    )
    mat_black = get_or_create_material(
        "FCD_Black_HW", base_color=(0.05, 0.05, 0.05, 1.0), metallic=0.5, roughness=0.4
    )
    mat_rubber = get_or_create_material(
        "FCD_Rubber", base_color=(0.05, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.95
    )

    w, d, h = dims.ext_w, dims.ext_d, dims.ext_h
    t       = dims.ply_t
    sz      = dims.split_z

    has_lid  = case_props.case_type not in ("CUSTOM_BOX",)
    is_rack  = case_props.case_type == "RACK_CASE"
    hinged   = case_props.case_type == "HINGED_LID"

    # ------------------------------------------------------------------ #
    # Latches
    # ------------------------------------------------------------------ #
    if hdw_props.latch_type != "NONE" and has_lid:
        latch_w, latch_d, latch_h = 0.060, 0.012, 0.040
        n = hdw_props.latch_count or dims.auto_latch_count()
        positions = _even_positions(w, n, latch_w)
        for i, lx in enumerate(positions):
            loc = (lx, -latch_d, sz - latch_h / 2.0)
            obj = _hw_box(f"Latch_{i:02d}", latch_w, latch_d, latch_h, loc, mat_chrome)
            link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Handles
    # ------------------------------------------------------------------ #
    if hdw_props.handle_type != "NONE":
        handle_w, handle_d, handle_h = 0.150, 0.050, 0.040
        n = hdw_props.handle_count or dims.auto_handle_count()
        handle_z = h / 2.0 - handle_h / 2.0
        for i in range(n):
            # Left side
            ly = (d - handle_w) / 2.0 if n == 1 else (d / 4.0 * (i + 1) - handle_w / 2.0)
            obj_l = _hw_box(
                f"Handle_L_{i:02d}", handle_d, handle_w, handle_h,
                loc=(-handle_d, ly, handle_z), material=mat_black
            )
            link_object(obj_l, hw_col)
            # Right side
            obj_r = _hw_box(
                f"Handle_R_{i:02d}", handle_d, handle_w, handle_h,
                loc=(w, ly, handle_z), material=mat_black
            )
            link_object(obj_r, hw_col)

    # ------------------------------------------------------------------ #
    # Corner hardware
    # ------------------------------------------------------------------ #
    if case_props.corner_type != "NONE":
        cs = 0.038  # corner size ~ 38 mm
        ct = 0.006  # corner thickness
        mat_c = mat_chrome if case_props.corner_type == "BALL" else mat_black
        corners_z = [0.0, h - cs]  # bottom and top rings
        corners_xy = [
            (0,     0),
            (w - cs, 0),
            (w - cs, d - cs),
            (0,     d - cs),
        ]
        for cz in corners_z:
            for idx, (cx, cy) in enumerate(corners_xy):
                obj = _hw_box(
                    f"Corner_{int(cz*100):04d}_{idx:02d}",
                    cs, cs, cs, loc=(cx, cy, cz), material=mat_c
                )
                link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Feet / Casters
    # ------------------------------------------------------------------ #
    if hdw_props.feet_type != "NONE":
        foot_r  = 0.018  # radius
        foot_h  = 0.020 if hdw_props.feet_type == "RUBBER" else 0.065
        foot_mat = mat_rubber if hdw_props.feet_type == "RUBBER" else mat_black
        margin = 0.040
        foot_positions = [
            (margin,     margin),
            (w - margin, margin),
            (w - margin, d - margin),
            (margin,     d - margin),
        ]
        for fi, (fx, fy) in enumerate(foot_positions):
            obj = _hw_cyl(
                f"Foot_{fi:02d}", foot_r, foot_h,
                loc=(fx, fy, -foot_h), mat=foot_mat
            )
            link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Hinges (hinged-lid only)
    # ------------------------------------------------------------------ #
    if hinged and has_lid:
        hinge_w, hinge_d, hinge_h = 0.060, 0.006, 0.080
        n_hinges = hdw_props.hinge_count
        positions = _even_positions(w, n_hinges, hinge_w)
        for i, hx in enumerate(positions):
            obj = _hw_box(
                f"Hinge_{i:02d}", hinge_w, hinge_d, hinge_h,
                loc=(hx, d - hinge_d, sz - hinge_h / 2.0), material=mat_chrome
            )
            link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Stacking cups
    # ------------------------------------------------------------------ #
    if hdw_props.stacking_cups:
        cup_r  = 0.025
        cup_h  = 0.015
        margin = 0.050
        cup_positions = [
            (margin,     margin),
            (w - margin, margin),
            (w - margin, d - margin),
            (margin,     d - margin),
        ]
        for ci, (cx, cy) in enumerate(cup_positions):
            obj = _hw_cyl(
                f"StackCup_{ci:02d}", cup_r, cup_h,
                loc=(cx, cy, h), mat=mat_black
            )
            link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Label holder
    # ------------------------------------------------------------------ #
    if hdw_props.label_holder and has_lid:
        lbl_w, lbl_d, lbl_h = 0.080, 0.003, 0.050
        lbl_x = (w - lbl_w) / 2.0
        lbl_z = sz * 0.35
        obj = _hw_box(
            "LabelHolder", lbl_w, lbl_d, lbl_h,
            loc=(lbl_x, -lbl_d, lbl_z), material=mat_chrome
        )
        link_object(obj, hw_col)

    # ------------------------------------------------------------------ #
    # Rack rails (rack case only)
    # ------------------------------------------------------------------ #
    if is_rack:
        rail_w, rail_d, rail_h = 0.015, 0.006, dims.int_h
        for side_x in (t, w - t - rail_w):
            obj = _hw_box(
                f"RackRail_{'L' if side_x < w/2 else 'R'}",
                rail_w, rail_d, rail_h,
                loc=(side_x, t, t), material=mat_chrome
            )
            link_object(obj, hw_col)
