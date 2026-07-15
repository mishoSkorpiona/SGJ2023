# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-level bmesh / object helpers shared by all generators."""

from __future__ import annotations

from typing import Sequence, Tuple

import bpy
import bmesh
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def mm(value: float) -> float:
    """Convert millimetres to Blender metres."""
    return value / 1000.0


# ---------------------------------------------------------------------------
# Object / collection helpers
# ---------------------------------------------------------------------------

def ensure_collection(parent: bpy.types.Collection, name: str) -> bpy.types.Collection:
    """Return a child collection of *parent*, creating it if it does not exist."""
    for child in parent.children:
        if child.name == name:
            return child
    col = bpy.data.collections.new(name)
    parent.children.link(col)
    return col


def clear_collection(col: bpy.types.Collection) -> None:
    """Delete every object in *col* and all its descendant collections."""
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in list(col.children):
        clear_collection(child)


def link_object(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    """Unlink *obj* from every current collection then link it to *col*."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def get_or_create_root_collection(name: str) -> bpy.types.Collection:
    """Return the named top-level collection, creating and scene-linking it if needed."""
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
    scene_col = bpy.context.scene.collection
    if col.name not in [c.name for c in scene_col.children]:
        scene_col.children.link(col)
    return col


# ---------------------------------------------------------------------------
# Material helpers
# ---------------------------------------------------------------------------

def get_or_create_material(
    name: str,
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.7,
    alpha: float = 1.0,
) -> bpy.types.Material:
    """Return existing material or create a new Principled BSDF one."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = base_color
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness
            if alpha < 1.0:
                bsdf.inputs["Alpha"].default_value = alpha
                mat.blend_method = "BLEND"
    return mat


# ---------------------------------------------------------------------------
# Mesh creation primitives
# ---------------------------------------------------------------------------

def create_box_mesh(
    name: str,
    width: float,
    depth: float,
    height: float,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """
    Create a solid box mesh object.

    Parameters
    ----------
    name:     Object / mesh name.
    width:    Extent along the local X axis (metres).
    depth:    Extent along the local Y axis (metres).
    height:   Extent along the local Z axis (metres).
    location: World-space origin of the box *bottom-left-front* corner.
    material: Optional material to assign.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Build the 8 vertices of the box
    verts = [
        bm.verts.new((0,     0,      0)),
        bm.verts.new((width, 0,      0)),
        bm.verts.new((width, depth,  0)),
        bm.verts.new((0,     depth,  0)),
        bm.verts.new((0,     0,      height)),
        bm.verts.new((width, 0,      height)),
        bm.verts.new((width, depth,  height)),
        bm.verts.new((0,     depth,  height)),
    ]
    bm.verts.ensure_lookup_table()

    faces = [
        (0, 3, 2, 1),  # bottom  (-Z)
        (4, 5, 6, 7),  # top     (+Z)
        (0, 1, 5, 4),  # front   (-Y)
        (2, 3, 7, 6),  # back    (+Y)
        (0, 4, 7, 3),  # left    (-X)
        (1, 2, 6, 5),  # right   (+X)
    ]
    for fv in faces:
        bm.faces.new([verts[i] for i in fv])

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location

    if material is not None:
        obj.data.materials.append(material)

    return obj


def create_flat_panel(
    name: str,
    width: float,
    depth: float,
    thickness: float,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """
    Thin box alias – thickness along Z.  Equivalent to
    ``create_box_mesh(name, width, depth, thickness, location, material)``.
    """
    return create_box_mesh(name, width, depth, thickness, location, material)


def create_cylinder(
    name: str,
    radius: float,
    depth: float,
    segments: int = 12,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Create a Z-aligned cylinder mesh object."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cylinder(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    if material is not None:
        obj.data.materials.append(material)
    return obj


def create_sphere(
    name: str,
    radius: float,
    segments: int = 12,
    rings: int = 8,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Create a UV-sphere mesh object."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=segments,
        v_segments=rings,
        radius=radius,
    )
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    if material is not None:
        obj.data.materials.append(material)
    return obj


def extrude_profile_along_path(
    name: str,
    cross_section_verts: Sequence[Tuple[float, float]],
    path_start: Vector,
    path_end: Vector,
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """
    Extrude a 2-D cross section (XY) along a straight path (path_start → path_end).

    The path direction replaces the local Z axis of the extrusion.
    """
    path_vec = path_end - path_start
    length = path_vec.length
    if length < 1e-9:
        return None  # degenerate

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    n = len(cross_section_verts)
    # Bottom ring (at path_start)
    bot_verts = [bm.verts.new((v[0], v[1], 0.0)) for v in cross_section_verts]
    # Top ring (at path_end)
    top_verts = [bm.verts.new((v[0], v[1], length)) for v in cross_section_verts]

    bm.verts.ensure_lookup_table()

    # Side faces
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([bot_verts[i], bot_verts[j], top_verts[j], top_verts[i]])

    # Cap faces
    bm.faces.new(bot_verts[::-1])  # bottom cap (normal points -Z)
    bm.faces.new(top_verts)        # top cap    (normal points +Z)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)

    # Orient the object so local Z aligns with path_vec
    z_axis = Vector((0, 0, 1))
    direction = path_vec.normalized()
    rot = z_axis.rotation_difference(direction).to_matrix().to_4x4()
    obj.matrix_world = Matrix.Translation(path_start) @ rot

    if material is not None:
        obj.data.materials.append(material)
    return obj
