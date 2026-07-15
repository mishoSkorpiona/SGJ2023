"""
geometry/foam_generator.py — Foam block generation with optional cutouts.

Generates:
  * Simple foam blocks per side (top/bottom/left/right/front/back).
  * Boolean cutout for equipment form-fit.
  * Finger pull notches.
  * Cable channel routing.
  * Multi-layer foam stacks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import bmesh
import mathutils

from ..utils.math_utils import mm_to_m
from ..utils.mesh_utils import (
    bmesh_box,
    apply_bmesh_to_object,
    get_or_create_mesh_object,
    boolean_difference,
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

def generate_foam(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
) -> None:
    """Create or update all foam objects for the case."""
    project_name = params.project_name
    foam_col = get_sub_collection(project_name, "Foam")
    if foam_col is None:
        foam_col = ensure_collection(f"{project_name}_Foam")

    eq = params.equipment
    mat = params.material
    foam = params.foam
    t_mm = mat.thickness_mm
    t = mm_to_m(t_mm)

    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)

    # Foam thickness per face
    if foam.asymmetric:
        ft = {
            "top":    mm_to_m(foam.top),
            "bottom": mm_to_m(foam.bottom),
            "front":  mm_to_m(foam.front),
            "back":   mm_to_m(foam.back),
            "left":   mm_to_m(foam.left),
            "right":  mm_to_m(foam.right),
        }
    else:
        uniform = mm_to_m(foam.bottom)
        ft = {k: uniform for k in ("top", "bottom", "front", "back", "left", "right")}

    # Bottom foam
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Bottom",
        width=int_w, depth=int_d, height=ft["bottom"],
        location=mathutils.Vector((0, 0, t + ft["bottom"] / 2)),
    )

    # Top foam (inside lid)
    ext_h = int_h + t * 2
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Top",
        width=int_w, depth=int_d, height=ft["top"],
        location=mathutils.Vector((0, 0, ext_h - t - ft["top"] / 2)),
    )

    # Left foam
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Left",
        width=ft["left"], depth=int_d, height=int_h - ft["top"] - ft["bottom"],
        location=mathutils.Vector((
            -(int_w / 2 - ft["left"] / 2),
            0,
            t + ft["bottom"] + (int_h - ft["top"] - ft["bottom"]) / 2,
        )),
    )

    # Right foam
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Right",
        width=ft["right"], depth=int_d, height=int_h - ft["top"] - ft["bottom"],
        location=mathutils.Vector((
            int_w / 2 - ft["right"] / 2,
            0,
            t + ft["bottom"] + (int_h - ft["top"] - ft["bottom"]) / 2,
        )),
    )

    # Front foam
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Front",
        width=int_w - ft["left"] - ft["right"],
        depth=ft["front"],
        height=int_h - ft["top"] - ft["bottom"],
        location=mathutils.Vector((
            0,
            -(int_d / 2 - ft["front"] / 2),
            t + ft["bottom"] + (int_h - ft["top"] - ft["bottom"]) / 2,
        )),
    )

    # Back foam
    _make_foam_block(
        foam_col, root_obj, project_name, "Foam_Back",
        width=int_w - ft["left"] - ft["right"],
        depth=ft["back"],
        height=int_h - ft["top"] - ft["bottom"],
        location=mathutils.Vector((
            0,
            int_d / 2 - ft["back"] / 2,
            t + ft["bottom"] + (int_h - ft["top"] - ft["bottom"]) / 2,
        )),
    )

    # Equipment form-fit cutout on bottom foam
    if eq.width > 0 and eq.height > 0 and eq.depth > 0:
        _apply_equipment_cutout(foam_col, root_obj, project_name, params, context, t, ft)

    # Finger pull notches
    if foam.finger_pulls:
        _add_finger_pulls(foam_col, root_obj, project_name, params, context, int_w, int_d, t, ft)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_foam_block(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    name: str,
    width: float,
    depth: float,
    height: float,
    location: mathutils.Vector,
) -> bpy.types.Object:
    full_name = f"{project_name}_{name}"
    obj = get_or_create_mesh_object(full_name, collection)
    bm = bmesh.new()
    bmesh_box(bm, width, height, depth)
    apply_bmesh_to_object(bm, obj)
    bm.free()
    obj.location = location
    set_fc_type(obj, "foam")
    parent_object(obj, root_obj)
    link_to_collection(obj, collection)
    return obj


def _apply_equipment_cutout(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    params: "CaseSettings",
    context: bpy.types.Context,
    t: float,
    ft: dict,
) -> None:
    """Boolean-subtract equipment silhouette from bottom foam."""
    eq = params.equipment
    eq_w = mm_to_m(eq.width)
    eq_d = mm_to_m(eq.depth)
    eq_h = mm_to_m(eq.height)

    # Create a temporary cutter object
    cutter_name = f"{project_name}_EqCutter"
    cutter_mesh = bpy.data.meshes.new(cutter_name)
    cutter_obj = bpy.data.objects.new(cutter_name, cutter_mesh)
    collection.objects.link(cutter_obj)

    bm = bmesh.new()
    bmesh_box(bm, eq_w, eq_h + ft["bottom"] * 0.5, eq_d)
    apply_bmesh_to_object(bm, obj=cutter_obj)
    bm.free()

    cutter_obj.location = mathutils.Vector((0, 0, t + ft["bottom"] / 2))

    bottom_foam_name = f"{project_name}_Foam_Bottom"
    if bottom_foam_name in bpy.data.objects:
        target = bpy.data.objects[bottom_foam_name]
        boolean_difference(target, cutter_obj, context)

    bpy.data.objects.remove(cutter_obj, do_unlink=True)
    bpy.data.meshes.remove(cutter_mesh)


def _add_finger_pulls(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    params: "CaseSettings",
    context: bpy.types.Context,
    int_w: float,
    int_d: float,
    t: float,
    ft: dict,
) -> None:
    """Subtract small finger-pull notches at the front edge of bottom foam."""
    pull_w = mm_to_m(40.0)
    pull_d = mm_to_m(30.0)
    pull_h = mm_to_m(20.0)

    notch_name = f"{project_name}_FingerPullCutter"
    mesh = bpy.data.meshes.new(notch_name)
    cutter = bpy.data.objects.new(notch_name, mesh)
    collection.objects.link(cutter)

    bm = bmesh.new()
    bmesh_box(bm, pull_w, pull_h * 2, pull_d)
    apply_bmesh_to_object(bm, cutter)
    bm.free()

    cutter.location = mathutils.Vector((0, -(int_d / 2 - pull_d / 2), t + ft["bottom"] / 2))

    bottom_foam_name = f"{project_name}_Foam_Bottom"
    if bottom_foam_name in bpy.data.objects:
        boolean_difference(bpy.data.objects[bottom_foam_name], cutter, context)

    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh)
