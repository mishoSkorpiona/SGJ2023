"""
drawings/drawing_generator.py — Orthographic and technical drawing generator.

Creates Blender camera rigs for:
  * Top view
  * Front view
  * Side (right) view
  * Section view (mid-depth cut)
  * Exploded view (objects offset outward)
  * Assembly view (all objects at correct positions)

Each view is represented as a named camera object parented to the case root.
Render output paths are tagged on the cameras so the export panel can render
them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import mathutils

if TYPE_CHECKING:
    from ..core.parameters import CaseSettings


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_drawings(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
) -> None:
    """Create or update all drawing cameras for the case."""
    from ..utils.math_utils import mm_to_m

    eq = params.equipment
    mat = params.material
    t = mm_to_m(mat.thickness_mm)
    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)
    ext_w = int_w + t * 2
    ext_d = int_d + t * 2
    ext_h = int_h + t * 2

    centre = mathutils.Vector((0, 0, ext_h / 2))
    dist = max(ext_w, ext_d, ext_h) * 3.0

    views = {
        "DrawingCam_Top":    (centre + mathutils.Vector((0,  0,  dist)),
                              mathutils.Euler((0,      0,      0))),
        "DrawingCam_Front":  (centre + mathutils.Vector((0, -dist, 0)),
                              mathutils.Euler((1.5708, 0,      0))),
        "DrawingCam_Right":  (centre + mathutils.Vector((dist, 0, 0)),
                              mathutils.Euler((1.5708, 0,      1.5708))),
        "DrawingCam_Section":(centre + mathutils.Vector((dist * 0.5, -dist, 0)),
                              mathutils.Euler((1.5708, 0,      0))),
    }

    for cam_name, (location, rotation) in views.items():
        full_name = f"{params.project_name}_{cam_name}"
        _ensure_ortho_camera(full_name, location, rotation, root_obj, context)


def generate_exploded_view(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
    explode_factor: float = 2.0,
) -> None:
    """Offset all child objects outward from the case centre for an exploded view."""
    centre = mathutils.Vector((0, 0, 0))
    for child in root_obj.children:
        if child.type != "MESH":
            continue
        direction = (child.location - centre)
        if direction.length < 1e-6:
            direction = mathutils.Vector((0, 0, 1))
        else:
            direction = direction.normalized()
        child["fc_exploded_offset"] = list(direction * explode_factor)
        child.location = child.location + direction * explode_factor


def reset_exploded_view(root_obj: bpy.types.Object) -> None:
    """Restore all child objects to their non-exploded positions."""
    for child in root_obj.children:
        offset = child.get("fc_exploded_offset")
        if offset:
            child.location = child.location - mathutils.Vector(offset)
            del child["fc_exploded_offset"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_ortho_camera(
    name: str,
    location: mathutils.Vector,
    rotation: mathutils.Euler,
    root_obj: bpy.types.Object,
    context: bpy.types.Context,
) -> bpy.types.Object:
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
    else:
        cam_data = bpy.data.cameras.new(name)
        cam_data.type = "ORTHO"
        cam_obj = bpy.data.objects.new(name, cam_data)
        context.scene.collection.objects.link(cam_obj)

    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    if isinstance(cam_obj.data, bpy.types.Camera):
        cam_obj.data.type = "ORTHO"
    cam_obj.parent = root_obj
    cam_obj["fc_type"] = "drawing_camera"
    return cam_obj
