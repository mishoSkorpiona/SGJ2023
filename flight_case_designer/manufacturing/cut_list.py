"""
manufacturing/cut_list.py — Panel and profile cut list builder.

Extracts bounding-box dimensions from each panel and profile object and
appends them to CaseData.panels / CaseData.profile_cuts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def build_cut_list(data: "CaseData", root_obj: bpy.types.Object) -> None:
    """Populate *data* with panel and profile cut dimensions."""
    collection_name = root_obj.get("flight_case_collection", "")
    if not collection_name or collection_name not in bpy.data.collections:
        return

    col = bpy.data.collections[collection_name]
    all_objects = list(col.all_objects)
    params = root_obj.flight_case
    t_mm = params.material.thickness_mm

    for obj in all_objects:
        fc_type = obj.get("fc_type")
        if fc_type == "panel" and obj.data:
            bb = obj.bound_box
            dims = sorted([
                (max(v[0] for v in bb) - min(v[0] for v in bb)) * 1000,
                (max(v[1] for v in bb) - min(v[1] for v in bb)) * 1000,
                (max(v[2] for v in bb) - min(v[2] for v in bb)) * 1000,
            ], reverse=True)
            # Largest two dims are W × H; smallest is thickness
            data.panels.append({
                "name": obj.name,
                "width_mm": round(dims[0], 1),
                "height_mm": round(dims[1], 1),
                "thickness_mm": round(t_mm, 1),
                "material": params.material.plywood_type,
                "qty": 1,
            })

        elif fc_type == "profile" and obj.data:
            bb = obj.bound_box
            dims = sorted([
                (max(v[0] for v in bb) - min(v[0] for v in bb)) * 1000,
                (max(v[1] for v in bb) - min(v[1] for v in bb)) * 1000,
                (max(v[2] for v in bb) - min(v[2] for v in bb)) * 1000,
            ], reverse=True)
            data.profile_cuts.append({
                "name": obj.name,
                "profile_type": params.profile.profile_type,
                "length_mm": round(dims[0], 1),
                "qty": 1,
            })
