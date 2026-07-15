"""
utils/object_utils.py — Object hierarchy, naming, and collection utilities.
"""

from __future__ import annotations

import bpy


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------

def ensure_collection(
    name: str, parent: bpy.types.Collection = None
) -> bpy.types.Collection:
    """Return an existing collection named *name*, or create it under *parent*."""
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(col)
    else:
        parent.children.link(col)
    return col


def ensure_case_collection(
    project_name: str, context: bpy.types.Context
) -> bpy.types.Collection:
    """
    Ensure a top-level collection named *project_name* with sub-collections:
    Panels, Profiles, Hardware, Foam, Rivets, Supports.
    """
    root_col = ensure_collection(project_name)
    for sub in ("Panels", "Profiles", "Hardware", "Foam", "Rivets", "Supports"):
        ensure_collection(f"{project_name}_{sub}", parent=root_col)
    return root_col


def get_sub_collection(
    project_name: str, sub_name: str
) -> bpy.types.Collection | None:
    """Return the sub-collection ``{project_name}_{sub_name}`` if it exists."""
    key = f"{project_name}_{sub_name}"
    return bpy.data.collections.get(key)


def clear_collection_objects(col: bpy.types.Collection) -> None:
    """Remove all mesh objects from *col* (does not recurse into children)."""
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


# ---------------------------------------------------------------------------
# Object linking helpers
# ---------------------------------------------------------------------------

def link_to_collection(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    """Link *obj* to *collection*, unlinking from scene root if present."""
    scene_col = bpy.context.scene.collection
    if obj.name in scene_col.objects:
        scene_col.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

def unique_name(base: str) -> str:
    """Return *base* if no object with that name exists, else *base*.001 etc."""
    if base not in bpy.data.objects:
        return base
    i = 1
    while True:
        candidate = f"{base}.{i:03d}"
        if candidate not in bpy.data.objects:
            return candidate
        i += 1


def set_fc_type(obj: bpy.types.Object, fc_type: str) -> None:
    """Tag an object with its flight-case sub-system type."""
    obj["fc_type"] = fc_type


# ---------------------------------------------------------------------------
# Parent / child helpers
# ---------------------------------------------------------------------------

def parent_object(
    child: bpy.types.Object, parent: bpy.types.Object
) -> None:
    """Parent *child* to *parent* without keeping transform."""
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
