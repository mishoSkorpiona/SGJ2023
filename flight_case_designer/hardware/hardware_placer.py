"""
hardware/hardware_placer.py — Rule-based automatic hardware placement.

Placement rules
---------------
* Butterfly latches: 1 per front/back edge up to 500 mm; 2 beyond that; 3 beyond 900 mm.
* Spring handles: 1 per side up to 600 mm wide; 2 beyond that.
* Ball / cast corners: always at 8 box corners.
* Hinges: 2 on back edge of lid (when hinged lid template).
* Rubber feet: 4 at base corners.
* Casters: 4 at base corners (when heavy / trunk case).
* Rack rails: 2 vertical strips on left/right interior (rack case only).

Manual overrides are respected — if a hardware object with the same name
already exists and has ``fc_manual_override = True``, its position is kept.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import bpy
import bmesh
import mathutils

from ..utils.math_utils import mm_to_m
from ..utils.mesh_utils import apply_bmesh_to_object, get_or_create_mesh_object
from ..utils.object_utils import (
    get_sub_collection,
    ensure_collection,
    set_fc_type,
    parent_object,
    link_to_collection,
)
from .hardware_library import HardwareLibrary, HardwareDefinition

if TYPE_CHECKING:
    from ..core.parameters import CaseSettings


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def place_hardware(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
) -> None:
    """Create or update all hardware objects according to placement rules."""
    project_name = params.project_name
    hw_col = get_sub_collection(project_name, "Hardware")
    if hw_col is None:
        hw_col = ensure_collection(f"{project_name}_Hardware")

    eq = params.equipment
    mat = params.material
    hw_params = params.hardware
    t_mm = mat.thickness_mm
    t = mm_to_m(t_mm)

    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)
    ext_w = int_w + t * 2
    ext_d = int_d + t * 2
    ext_h = int_h + t * 2
    weight = eq.weight

    placements: List[dict] = []

    if hw_params.butterfly_latches:
        placements += _latch_placements(ext_w, ext_d, ext_h, t, weight)

    if hw_params.spring_handles:
        placements += _handle_placements(ext_w, ext_d, ext_h, t, weight)

    if hw_params.ball_corners or hw_params.cast_corners:
        hw_name = "cast_corner" if hw_params.cast_corners else "ball_corner"
        placements += _corner_placements(ext_w, ext_d, ext_h, t, hw_name)

    if hw_params.hinges:
        placements += _hinge_placements(ext_w, ext_d, ext_h, t)

    if hw_params.rubber_feet:
        placements += _rubber_foot_placements(ext_w, ext_d, t)

    if hw_params.casters:
        placements += _caster_placements(ext_w, ext_d, t)

    if hw_params.rack_rails:
        placements += _rack_rail_placements(int_w, int_d, int_h, t, params.rack_units)

    for idx, placement in enumerate(placements):
        _create_hardware_object(
            hw_col, root_obj, project_name, idx, placement, context
        )


# ---------------------------------------------------------------------------
# Placement rule helpers
# ---------------------------------------------------------------------------

def _latch_placements(
    ext_w: float, ext_d: float, ext_h: float, t: float, weight: float
) -> List[dict]:
    w_mm = ext_w * 1000
    count = 1
    if w_mm > 500:
        count = 2
    if w_mm > 900:
        count = 3

    def_name = "butterfly_latch"
    hw = HardwareLibrary.get(def_name)
    if hw is None:
        return []

    hw_h_m = mm_to_m(hw.height_mm)
    y_front = -ext_d / 2 - mm_to_m(hw.depth_mm) / 2
    y_back  =  ext_d / 2 + mm_to_m(hw.depth_mm) / 2
    z       =  ext_h * 0.65  # place at 65 % height (lid split zone)

    placements = []
    if count == 1:
        xs = [0.0]
    elif count == 2:
        xs = [-ext_w * 0.25, ext_w * 0.25]
    else:
        xs = [-ext_w * 0.33, 0.0, ext_w * 0.33]

    for x in xs:
        for y, rot in ((y_front, 0.0), (y_back, 3.14159)):
            placements.append({
                "hw_name": def_name,
                "location": mathutils.Vector((x, y, z)),
                "rotation": mathutils.Euler((0, 0, rot)),
            })
    return placements


def _handle_placements(
    ext_w: float, ext_d: float, ext_h: float, t: float, weight: float
) -> List[dict]:
    w_mm = ext_w * 1000
    count = 1 if w_mm <= 600 else 2

    def_name = "spring_handle"
    hw = HardwareLibrary.get(def_name)
    if hw is None:
        return []

    y = -ext_d / 2 - mm_to_m(hw.depth_mm) / 2
    z = ext_h * 0.5

    xs = [0.0] if count == 1 else [-ext_w * 0.25, ext_w * 0.25]
    return [
        {"hw_name": def_name, "location": mathutils.Vector((x, y, z)),
         "rotation": mathutils.Euler((0, 0, 0))}
        for x in xs
    ]


def _corner_placements(
    ext_w: float, ext_d: float, ext_h: float, t: float, hw_name: str
) -> List[dict]:
    hw = HardwareLibrary.get(hw_name)
    if hw is None:
        return []
    hw_s = mm_to_m(hw.width_mm) / 2
    corners = [
        (-ext_w / 2, -ext_d / 2, 0),
        ( ext_w / 2, -ext_d / 2, 0),
        (-ext_w / 2,  ext_d / 2, 0),
        ( ext_w / 2,  ext_d / 2, 0),
        (-ext_w / 2, -ext_d / 2, ext_h),
        ( ext_w / 2, -ext_d / 2, ext_h),
        (-ext_w / 2,  ext_d / 2, ext_h),
        ( ext_w / 2,  ext_d / 2, ext_h),
    ]
    return [
        {"hw_name": hw_name, "location": mathutils.Vector(c),
         "rotation": mathutils.Euler((0, 0, 0))}
        for c in corners
    ]


def _hinge_placements(
    ext_w: float, ext_d: float, ext_h: float, t: float
) -> List[dict]:
    hw = HardwareLibrary.get("hinge")
    if hw is None:
        return []
    y = ext_d / 2
    z = ext_h * 0.65
    return [
        {"hw_name": "hinge",
         "location": mathutils.Vector((x, y, z)),
         "rotation": mathutils.Euler((0, 0, 0))}
        for x in (-ext_w * 0.25, ext_w * 0.25)
    ]


def _rubber_foot_placements(
    ext_w: float, ext_d: float, t: float
) -> List[dict]:
    hw = HardwareLibrary.get("rubber_foot")
    if hw is None:
        return []
    margin = mm_to_m(30.0)
    h_m = mm_to_m(hw.height_mm)
    return [
        {"hw_name": "rubber_foot",
         "location": mathutils.Vector((x, y, -h_m / 2)),
         "rotation": mathutils.Euler((0, 0, 0))}
        for x in (-ext_w / 2 + margin, ext_w / 2 - margin)
        for y in (-ext_d / 2 + margin, ext_d / 2 - margin)
    ]


def _caster_placements(
    ext_w: float, ext_d: float, t: float
) -> List[dict]:
    hw = HardwareLibrary.get("caster")
    if hw is None:
        return []
    margin = mm_to_m(40.0)
    h_m = mm_to_m(hw.height_mm)
    return [
        {"hw_name": "caster",
         "location": mathutils.Vector((x, y, -h_m / 2)),
         "rotation": mathutils.Euler((0, 0, 0))}
        for x in (-ext_w / 2 + margin, ext_w / 2 - margin)
        for y in (-ext_d / 2 + margin, ext_d / 2 - margin)
    ]


def _rack_rail_placements(
    int_w: float, int_d: float, int_h: float, t: float, rack_units: int
) -> List[dict]:
    hw = HardwareLibrary.get("rack_rail")
    if hw is None:
        return []
    rail_x = int_w / 2 - mm_to_m(hw.width_mm) / 2
    return [
        {"hw_name": "rack_rail",
         "location": mathutils.Vector((x, 0, t + int_h / 2)),
         "rotation": mathutils.Euler((0, 0, 0))}
        for x in (-rail_x, rail_x)
    ]


# ---------------------------------------------------------------------------
# Object creation helper
# ---------------------------------------------------------------------------

def _create_hardware_object(
    hw_col: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    idx: int,
    placement: dict,
    context: bpy.types.Context,
) -> bpy.types.Object:
    hw_def: HardwareDefinition = HardwareLibrary.get(placement["hw_name"])
    if hw_def is None:
        return None

    name = f"{project_name}_{placement['hw_name']}_{idx:03d}"
    obj = get_or_create_mesh_object(name, hw_col)

    if obj.get("fc_manual_override"):
        return obj

    bm = bmesh.new()
    hw_def.build_mesh(bm)
    apply_bmesh_to_object(bm, obj)
    bm.free()

    obj.location = placement["location"]
    obj.rotation_euler = placement["rotation"]
    set_fc_type(obj, "hardware")
    obj["hw_type"] = placement["hw_name"]
    parent_object(obj, root_obj)
    link_to_collection(obj, hw_col)
    return obj
