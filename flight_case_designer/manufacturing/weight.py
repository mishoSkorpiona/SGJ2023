"""
manufacturing/weight.py — Weight estimator.

Material densities (kg/m³):
  Birch plywood:    680
  Phenolic birch:   730
  MDF:              750
  EVA foam:          50
  PE foam:           30
  PU foam:           25
  Aluminium:       2700
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData

DENSITIES: dict[str, float] = {
    "BIRCH":    680.0,
    "PHENOLIC": 730.0,
    "MDF":      750.0,
    "EVA":       50.0,
    "PE":        30.0,
    "PU":        25.0,
    "ALUMINIUM": 2700.0,
}


def _volume_m3(obj: bpy.types.Object) -> float:
    """Return the approximate bounding-box volume of *obj* in m³."""
    bb = obj.bound_box
    w = max(v[0] for v in bb) - min(v[0] for v in bb)
    h = max(v[1] for v in bb) - min(v[1] for v in bb)
    d = max(v[2] for v in bb) - min(v[2] for v in bb)
    return w * h * d


def estimate_weight(data: "CaseData", root_obj: bpy.types.Object) -> float:
    """Return the total estimated weight in kg."""
    collection_name = root_obj.get("flight_case_collection", "")
    if not collection_name or collection_name not in bpy.data.collections:
        return 0.0

    col = bpy.data.collections[collection_name]
    all_objects = list(col.all_objects)
    params = root_obj.flight_case

    panel_density = DENSITIES.get(params.material.plywood_type, 680.0)
    foam_density = DENSITIES.get(params.foam.foam_type, 30.0)

    total = 0.0
    for obj in all_objects:
        fc_type = obj.get("fc_type")
        if fc_type == "panel":
            total += _volume_m3(obj) * panel_density
        elif fc_type in ("profile", "support"):
            total += _volume_m3(obj) * DENSITIES["ALUMINIUM"]
        elif fc_type == "foam":
            total += _volume_m3(obj) * foam_density

    # Add equipment weight
    total += params.equipment.weight

    return round(total, 2)
