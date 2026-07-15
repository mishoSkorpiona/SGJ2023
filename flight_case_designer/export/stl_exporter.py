"""
export/stl_exporter.py — Export case geometry as STL.

Uses Blender's built-in STL export operator.  Selected objects are exported
per-object, then all merged into a single STL file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def export(filepath: str, data: "CaseData", root_obj: bpy.types.Object = None) -> None:
    """Export case geometry to STL."""
    collection_name = data.project_name
    if collection_name not in bpy.data.collections:
        print(f"Collection '{collection_name}' not found.")
        return

    # Deselect all
    bpy.ops.object.select_all(action="DESELECT")

    col = bpy.data.collections[collection_name]
    for obj in col.all_objects:
        if obj.type == "MESH":
            obj.select_set(True)

    bpy.ops.wm.stl_export(
        filepath=filepath,
        export_selected_objects=True,
        global_scale=1.0,
    )
    bpy.ops.object.select_all(action="DESELECT")
    print(f"STL exported to {filepath}")
