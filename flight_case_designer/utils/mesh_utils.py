"""
utils/mesh_utils.py — BMesh helpers, boolean operations, and mesh utilities.
"""

from __future__ import annotations

from typing import List, Tuple

import bpy
import bmesh
import mathutils

from .math_utils import mm_to_m


# ---------------------------------------------------------------------------
# BMesh primitives
# ---------------------------------------------------------------------------

def bmesh_box(
    bm: bmesh.types.BMesh,
    width: float,
    height: float,
    depth: float,
    offset: mathutils.Vector = None,
) -> None:
    """
    Add a box primitive (in metres) to *bm*.

    *width* = X, *height* = Z, *depth* = Y.
    *offset* moves the box centre.
    """
    if offset is None:
        offset = mathutils.Vector((0, 0, 0))
    hw, hh, hd = width / 2, height / 2, depth / 2
    verts = [
        bm.verts.new(mathutils.Vector((offset.x + x, offset.y + y, offset.z + z)))
        for x in (-hw, hw)
        for y in (-hd, hd)
        for z in (-hh, hh)
    ]
    # Index layout: (−x−y−z)=0, (−x−y+z)=1, (−x+y−z)=2, (−x+y+z)=3,
    #               (+x−y−z)=4, (+x−y+z)=5, (+x+y−z)=6, (+x+y+z)=7
    face_indices = [
        (0, 1, 3, 2),   # −x face
        (4, 6, 7, 5),   # +x face
        (0, 4, 5, 1),   # −y face
        (2, 3, 7, 6),   # +y face
        (0, 2, 6, 4),   # −z face
        (1, 5, 7, 3),   # +z face
    ]
    for fi in face_indices:
        bm.faces.new([verts[i] for i in fi])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def bmesh_panel(
    bm: bmesh.types.BMesh,
    width: float,
    height: float,
    thickness: float,
    offset: mathutils.Vector = None,
) -> None:
    """Add a flat rectangular panel (thin box) to *bm*. All values in metres."""
    bmesh_box(bm, width, thickness, height, offset)


def apply_bmesh_to_object(
    bm: bmesh.types.BMesh, obj: bpy.types.Object
) -> None:
    """Write *bm* data into *obj*'s mesh, replacing existing geometry."""
    mesh = obj.data
    bm.to_mesh(mesh)
    mesh.update()


def get_or_create_mesh_object(
    name: str, collection: bpy.types.Collection
) -> bpy.types.Object:
    """
    Return an existing mesh object named *name* inside *collection*, or
    create a new one.
    """
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        if obj.data is None or not isinstance(obj.data, bpy.types.Mesh):
            mesh = bpy.data.meshes.new(name)
            obj.data = mesh
        return obj

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def boolean_difference(
    target: bpy.types.Object,
    cutter: bpy.types.Object,
    context: bpy.types.Context,
) -> None:
    """
    Apply a Boolean Difference modifier from *target* minus *cutter*.
    The modifier is applied immediately.
    """
    mod = target.modifiers.new("BoolDiff", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    mod.solver = "FAST"

    with context.temp_override(active_object=target):
        bpy.ops.object.modifier_apply(modifier=mod.name)


# ---------------------------------------------------------------------------
# Edge-sweep helper for profiles
# ---------------------------------------------------------------------------

def sweep_profile_along_edge(
    profile_verts_2d: List[Tuple[float, float]],
    start: mathutils.Vector,
    end: mathutils.Vector,
    bm: bmesh.types.BMesh,
) -> None:
    """
    Extrude a 2-D profile cross-section along the edge from *start* to *end*.

    *profile_verts_2d* is a list of (u, v) tuples defining the cross-section
    in the plane perpendicular to the edge direction.
    """
    edge_vec = end - start
    length = edge_vec.length
    if length < 1e-6:
        return

    direction = edge_vec.normalized()
    # Build a local coordinate frame
    up = mathutils.Vector((0, 0, 1))
    if abs(direction.dot(up)) > 0.99:
        up = mathutils.Vector((1, 0, 0))
    right = direction.cross(up).normalized()
    up = right.cross(direction).normalized()

    def make_ring(t: float) -> List[bmesh.types.BMVert]:
        pos = start + direction * t
        verts = []
        for u, v in profile_verts_2d:
            p = pos + right * u + up * v
            verts.append(bm.verts.new(p))
        return verts

    ring_a = make_ring(0.0)
    ring_b = make_ring(length)

    n = len(profile_verts_2d)
    for i in range(n):
        next_i = (i + 1) % n
        bm.faces.new([ring_a[i], ring_a[next_i], ring_b[next_i], ring_b[i]])

    # Cap faces
    bm.faces.new(ring_a)
    bm.faces.new(list(reversed(ring_b)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
