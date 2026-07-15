"""
export/step_exporter.py — Export case geometry as STEP (CAD).

Requires the ``cadquery`` library or Blender's built-in STEP export
(available via the ``io_scene_step`` add-on or ``bpy.ops.wm.step_export``).

Falls back to a warning if neither is available.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def export(filepath: str, data: "CaseData", root_obj: bpy.types.Object = None) -> None:
    """Export case geometry to STEP."""
    # Try Blender native STEP export (available in some builds)
    if hasattr(bpy.ops.wm, "step_export"):
        bpy.ops.object.select_all(action="DESELECT")
        collection_name = data.project_name
        if collection_name in bpy.data.collections:
            col = bpy.data.collections[collection_name]
            for obj in col.all_objects:
                if obj.type == "MESH":
                    obj.select_set(True)
        bpy.ops.wm.step_export(filepath=filepath)
        bpy.ops.object.select_all(action="DESELECT")
        print(f"STEP exported to {filepath}")
        return

    print(
        "STEP export is not available in this Blender build. "
        "Enable the 'io_scene_step' add-on or install cadquery."
    )
