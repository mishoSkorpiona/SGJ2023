"""
geometry/rivet_generator.py — Automatic rivet placement and mesh generation.

For every hardware item in the Hardware sub-collection, rivets are placed
around the item's mounting perimeter according to the RivetSettings.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

import bpy
import bmesh
import mathutils

from ..utils.math_utils import mm_to_m, distribute_evenly
from ..utils.mesh_utils import apply_bmesh_to_object, get_or_create_mesh_object
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
# Rivet mesh primitive
# ---------------------------------------------------------------------------

def _build_rivet_mesh(bm: bmesh.types.BMesh, radius: float, height: float) -> None:
    """Add a cylinder (rivet silhouette) to *bm*."""
    segments = 8
    verts_bot = []
    verts_top = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        verts_bot.append(bm.verts.new(mathutils.Vector((x, y, 0))))
        verts_top.append(bm.verts.new(mathutils.Vector((x, y, height))))
    # Side faces
    for i in range(segments):
        n = (i + 1) % segments
        bm.faces.new([verts_bot[i], verts_bot[n], verts_top[n], verts_top[i]])
    # Caps
    bm.faces.new(verts_bot)
    bm.faces.new(list(reversed(verts_top)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_rivets(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
) -> None:
    """Create or update rivet objects for all hardware items."""
    project_name = params.project_name
    rivet_col = get_sub_collection(project_name, "Rivets")
    if rivet_col is None:
        rivet_col = ensure_collection(f"{project_name}_Rivets")

    hw_col = get_sub_collection(project_name, "Hardware")
    if hw_col is None:
        return

    rivet_params = params.rivet
    radius = mm_to_m(rivet_params.diameter / 2)
    height = mm_to_m(1.5)
    spacing = rivet_params.spacing
    edge_offset = rivet_params.edge_offset

    # Prototype rivet mesh (shared across instances via a single object prototype)
    proto_name = f"{project_name}_Rivet_Proto"
    proto = get_or_create_mesh_object(proto_name, rivet_col)
    bm = bmesh.new()
    _build_rivet_mesh(bm, radius, height)
    apply_bmesh_to_object(bm, proto)
    bm.free()
    proto.hide_render = True
    proto.hide_viewport = False

    rivet_idx = 0
    for hw_obj in list(hw_col.objects):
        if hw_obj.get("fc_type") != "hardware":
            continue
        rivet_idx = _place_rivets_for_hardware(
            hw_obj, proto, rivet_col, root_obj, project_name,
            spacing, edge_offset, rivet_idx,
        )


def _place_rivets_for_hardware(
    hw_obj: bpy.types.Object,
    proto: bpy.types.Object,
    rivet_col: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    spacing: float,
    edge_offset: float,
    start_idx: int,
) -> int:
    """Place rivets around the perimeter of *hw_obj* and return the next index."""
    # Estimate from bounding box in local space
    bb = hw_obj.bound_box
    min_x = min(v[0] for v in bb)
    max_x = max(v[0] for v in bb)
    min_y = min(v[1] for v in bb)
    max_y = max(v[1] for v in bb)
    z_top = max(v[2] for v in bb)

    width_m = max_x - min_x
    depth_m = max_y - min_y

    width_mm = width_m * 1000.0
    depth_mm = depth_m * 1000.0

    positions_x = distribute_evenly(width_mm, spacing, edge_offset)
    positions_y = distribute_evenly(depth_mm, spacing, edge_offset)

    # Place along front/back edges (varying X)
    for y_side in (min_y, max_y):
        for x_pos in positions_x:
            x_m = min_x + x_pos / 1000.0
            loc = hw_obj.matrix_world @ mathutils.Vector((x_m, y_side, z_top))
            _instance_rivet(proto, rivet_col, root_obj, project_name, start_idx, loc)
            start_idx += 1

    # Place along left/right edges (varying Y)
    for x_side in (min_x, max_x):
        for y_pos in positions_y:
            y_m = min_y + y_pos / 1000.0
            loc = hw_obj.matrix_world @ mathutils.Vector((x_side, y_m, z_top))
            _instance_rivet(proto, rivet_col, root_obj, project_name, start_idx, loc)
            start_idx += 1

    return start_idx


def _instance_rivet(
    proto: bpy.types.Object,
    rivet_col: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    idx: int,
    location: mathutils.Vector,
) -> bpy.types.Object:
    """Create a rivet instance at *location*."""
    name = f"{project_name}_Rivet_{idx:04d}"
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
    else:
        obj = bpy.data.objects.new(name, proto.data)
        rivet_col.objects.link(obj)
    obj.location = location
    set_fc_type(obj, "rivet")
    parent_object(obj, root_obj)
    return obj
