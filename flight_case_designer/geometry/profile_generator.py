"""
geometry/profile_generator.py — Aluminium extrusion profile geometry.

Profiles are swept along panel edges.  The profile cross-section is looked up
from the profile library using the type stored in params.profile.profile_type.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

import bpy
import bmesh
import mathutils

from ..utils.math_utils import mm_to_m
from ..utils.mesh_utils import (
    sweep_profile_along_edge,
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

def generate_profiles(
    root_obj: bpy.types.Object,
    params: "CaseSettings",
    context: bpy.types.Context,
) -> None:
    """Create or update all aluminium extrusion profiles around the case."""
    from ..profiles.profile_library import ProfileLibrary

    project_name = params.project_name
    profile_col = get_sub_collection(project_name, "Profiles")
    if profile_col is None:
        profile_col = ensure_collection(f"{project_name}_Profiles")

    eq = params.equipment
    mat = params.material
    t_mm = mat.thickness_mm
    t = mm_to_m(t_mm)

    int_w = mm_to_m(eq.width + eq.internal_clearance * 2)
    int_d = mm_to_m(
        eq.depth + eq.cable_clearance + eq.connector_clearance + eq.internal_clearance * 2
    )
    int_h = mm_to_m(eq.height + eq.internal_clearance * 2)
    ext_w = int_w + t * 2
    ext_d = int_d + t * 2
    ext_h = int_h + t * 2

    profile_type = params.profile.profile_type
    if params.profile.custom_profile_name:
        profile_def = ProfileLibrary.get(params.profile.custom_profile_name)
    else:
        profile_def = ProfileLibrary.get(profile_type)

    if profile_def is None:
        return

    cross_section: List[Tuple[float, float]] = profile_def.cross_section_2d()

    # Define the 12 vertical and horizontal edges of the case box
    # Each edge: (start_xyz, end_xyz)
    hw = ext_w / 2
    hd = ext_d / 2

    vertical_edges = [
        (mathutils.Vector((-hw, -hd, 0)), mathutils.Vector((-hw, -hd, ext_h))),
        (mathutils.Vector(( hw, -hd, 0)), mathutils.Vector(( hw, -hd, ext_h))),
        (mathutils.Vector((-hw,  hd, 0)), mathutils.Vector((-hw,  hd, ext_h))),
        (mathutils.Vector(( hw,  hd, 0)), mathutils.Vector(( hw,  hd, ext_h))),
    ]
    horizontal_bottom = [
        (mathutils.Vector((-hw, -hd, 0)), mathutils.Vector(( hw, -hd, 0))),
        (mathutils.Vector((-hw,  hd, 0)), mathutils.Vector(( hw,  hd, 0))),
        (mathutils.Vector((-hw, -hd, 0)), mathutils.Vector((-hw,  hd, 0))),
        (mathutils.Vector(( hw, -hd, 0)), mathutils.Vector(( hw,  hd, 0))),
    ]
    horizontal_top = [
        (mathutils.Vector((-hw, -hd, ext_h)), mathutils.Vector(( hw, -hd, ext_h))),
        (mathutils.Vector((-hw,  hd, ext_h)), mathutils.Vector(( hw,  hd, ext_h))),
        (mathutils.Vector((-hw, -hd, ext_h)), mathutils.Vector((-hw,  hd, ext_h))),
        (mathutils.Vector(( hw, -hd, ext_h)), mathutils.Vector(( hw,  hd, ext_h))),
    ]

    all_edges = vertical_edges + horizontal_bottom + horizontal_top

    for idx, (start, end) in enumerate(all_edges):
        name = f"{project_name}_Profile_{idx:02d}"
        obj = get_or_create_mesh_object(name, profile_col)
        bm = bmesh.new()
        sweep_profile_along_edge(cross_section, start, end, bm)
        apply_bmesh_to_object(bm, obj)
        bm.free()
        set_fc_type(obj, "profile")
        parent_object(obj, root_obj)
        link_to_collection(obj, profile_col)
