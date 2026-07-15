"""
geometry/panel_generator.py — Generate case panels as mesh objects.

Panels produced:
  bottom, top, front, back, left, right

For cases with a separate lid the generator also produces:
  lid_top, lid_front, lid_back, lid_left, lid_right

Each panel is stored in the ``{project_name}_Panels`` collection and tagged
with ``fc_type = "panel"``.  The geometry is written directly into the mesh
data so the object identity is preserved across rebuilds.
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

def generate_panels(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
    lid_height_fraction: float = 0.35,
    has_lid: bool = True,
) -> None:
    """
    Create or update all case panels.

    Parameters
    ----------
    root_obj:
        The flight case root empty.
    params:
        The active CaseSettings property group.
    context:
        Current Blender context.
    lid_height_fraction:
        Height of the lid as a fraction of total case height (0–1).
    has_lid:
        Whether to generate a separate lid section.
    """
    project_name = params.project_name
    panel_col = get_sub_collection(project_name, "Panels")
    if panel_col is None:
        panel_col = ensure_collection(f"{project_name}_Panels")

    eq = params.equipment
    mat = params.material
    t_mm = mat.thickness_mm
    t = mm_to_m(t_mm)

    # Internal cavity dimensions in metres
    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)

    # External dimensions
    ext_w = int_w + t * 2
    ext_d = int_d + t * 2
    ext_h = int_h + t * 2

    lid_h = ext_h * lid_height_fraction if has_lid else 0.0
    base_h = ext_h - lid_h

    # ------------------------------------------------------------------
    # Base section panels
    # ------------------------------------------------------------------
    _make_panel(panel_col, root_obj, project_name,
                "Panel_Bottom",
                width=ext_w, depth=ext_d, thickness=t,
                location=mathutils.Vector((0, 0, t / 2)))

    _make_panel(panel_col, root_obj, project_name,
                "Panel_Front",
                width=ext_w, depth=t, thickness=base_h - t,
                location=mathutils.Vector((0, -(ext_d / 2 - t / 2), base_h / 2)))

    _make_panel(panel_col, root_obj, project_name,
                "Panel_Back",
                width=ext_w, depth=t, thickness=base_h - t,
                location=mathutils.Vector((0, ext_d / 2 - t / 2, base_h / 2)))

    _make_panel(panel_col, root_obj, project_name,
                "Panel_Left",
                width=t, depth=ext_d - t * 2, thickness=base_h - t,
                location=mathutils.Vector((-(ext_w / 2 - t / 2), 0, base_h / 2)))

    _make_panel(panel_col, root_obj, project_name,
                "Panel_Right",
                width=t, depth=ext_d - t * 2, thickness=base_h - t,
                location=mathutils.Vector((ext_w / 2 - t / 2, 0, base_h / 2)))

    # ------------------------------------------------------------------
    # Lid section panels (when applicable)
    # ------------------------------------------------------------------
    if has_lid:
        lid_z_base = base_h

        _make_panel(panel_col, root_obj, project_name,
                    "Panel_Lid_Top",
                    width=ext_w, depth=ext_d, thickness=t,
                    location=mathutils.Vector((0, 0, lid_z_base + lid_h - t / 2)))

        _make_panel(panel_col, root_obj, project_name,
                    "Panel_Lid_Front",
                    width=ext_w, depth=t, thickness=lid_h - t,
                    location=mathutils.Vector((0, -(ext_d / 2 - t / 2), lid_z_base + lid_h / 2)))

        _make_panel(panel_col, root_obj, project_name,
                    "Panel_Lid_Back",
                    width=ext_w, depth=t, thickness=lid_h - t,
                    location=mathutils.Vector((0, ext_d / 2 - t / 2, lid_z_base + lid_h / 2)))

        _make_panel(panel_col, root_obj, project_name,
                    "Panel_Lid_Left",
                    width=t, depth=ext_d - t * 2, thickness=lid_h - t,
                    location=mathutils.Vector((-(ext_w / 2 - t / 2), 0, lid_z_base + lid_h / 2)))

        _make_panel(panel_col, root_obj, project_name,
                    "Panel_Lid_Right",
                    width=t, depth=ext_d - t * 2, thickness=lid_h - t,
                    location=mathutils.Vector((ext_w / 2 - t / 2, 0, lid_z_base + lid_h / 2)))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _make_panel(
    collection: bpy.types.Collection,
    root_obj: bpy.types.Object,
    project_name: str,
    panel_name: str,
    width: float,
    depth: float,
    thickness: float,
    location: mathutils.Vector,
) -> bpy.types.Object:
    """Create or update a single panel mesh object."""
    full_name = f"{project_name}_{panel_name}"
    obj = get_or_create_mesh_object(full_name, collection)

    bm = bmesh.new()
    bmesh_box(bm, width, thickness, depth)
    apply_bmesh_to_object(bm, obj)
    bm.free()

    obj.location = location
    set_fc_type(obj, "panel")
    parent_object(obj, root_obj)
    link_to_collection(obj, collection)
    return obj
