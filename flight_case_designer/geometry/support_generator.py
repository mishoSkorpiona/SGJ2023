"""
geometry/support_generator.py — Internal support structure generation.

Generates:
  * Divider walls
  * Shelves
  * Rack rail supports
  * Braces
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import bmesh
import mathutils

from ..utils.math_utils import mm_to_m, rack_unit_height
from ..utils.mesh_utils import (
    bmesh_box,
    apply_bmesh_to_object,
    get_or_create_mesh_object,
)
from ..utils.object_utils import (
    get_sub_collection,
    ensure_collection,
    set_fc_type,
    parent_object,
    link_to_collection,
)

if TYPE_CHECKING:
    from ..core.parameters import CaseSettings


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_supports(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
    rack_units: int = 0,
    add_dividers: bool = False,
    add_shelves: bool = False,
) -> None:
    """Create or update internal support objects."""
    project_name = params.project_name
    support_col = get_sub_collection(project_name, "Supports")
    if support_col is None:
        support_col = ensure_collection(f"{project_name}_Supports")

    eq = params.equipment
    mat = params.material
    t_mm = mat.thickness_mm
    t = mm_to_m(t_mm)

    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)

    if rack_units > 0:
        _generate_rack_supports(
            support_col, root_obj, project_name, int_w, int_d, t, rack_units
        )

    if add_dividers:
        _generate_divider(
            support_col, root_obj, project_name,
            int_w, int_d, int_h, t,
        )

    if add_shelves:
        _generate_shelf(
            support_col, root_obj, project_name,
            int_w, int_d, int_h, t,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_rack_supports(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    int_w: float,
    int_d: float,
    t: float,
    rack_units: int,
) -> None:
    """Generate two vertical rack-rail support strips."""
    rail_w = mm_to_m(20.0)
    rail_h = mm_to_m(rack_unit_height(rack_units))
    rail_d = mm_to_m(5.0)
    y_offset = int_d / 2 - rail_d / 2

    for side, x_sign in (("Left", -1), ("Right", 1)):
        name = f"{project_name}_RackSupport_{side}"
        obj = get_or_create_mesh_object(name, collection)
        bm = bmesh.new()
        bmesh_box(bm, rail_w, rail_h, rail_d)
        apply_bmesh_to_object(bm, obj)
        bm.free()
        x = x_sign * (int_w / 2 - rail_w / 2)
        obj.location = mathutils.Vector((x, -y_offset, t + rail_h / 2))
        set_fc_type(obj, "support")
        parent_object(obj, root_obj)
        link_to_collection(obj, collection)


def _generate_divider(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    int_w: float,
    int_d: float,
    int_h: float,
    t: float,
) -> None:
    """Generate a single central vertical divider wall."""
    name = f"{project_name}_Divider"
    obj = get_or_create_mesh_object(name, collection)
    bm = bmesh.new()
    bmesh_box(bm, t / 2, int_h, int_d)
    apply_bmesh_to_object(bm, obj)
    bm.free()
    obj.location = mathutils.Vector((0, 0, t + int_h / 2))
    set_fc_type(obj, "support")
    parent_object(obj, root_obj)
    link_to_collection(obj, collection)


def _generate_shelf(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    int_w: float,
    int_d: float,
    int_h: float,
    t: float,
) -> None:
    """Generate a horizontal shelf at mid-height."""
    name = f"{project_name}_Shelf"
    obj = get_or_create_mesh_object(name, collection)
    bm = bmesh.new()
    bmesh_box(bm, int_w, t / 2, int_d)
    apply_bmesh_to_object(bm, obj)
    bm.free()
    obj.location = mathutils.Vector((0, 0, t + int_h / 2))
    set_fc_type(obj, "support")
    parent_object(obj, root_obj)
    link_to_collection(obj, collection)
