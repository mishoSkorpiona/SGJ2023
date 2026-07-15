"""
manufacturing/bom.py — Bill of Materials builder.

Traverses the case object hierarchy and populates a CaseData instance with:
  * Panel items (plywood sheets by size and material type).
  * Hardware items (count per type).
  * Profile cuts (length per profile type).
  * Foam items (volume per foam type).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def build_bom(data: "CaseData", root_obj: bpy.types.Object) -> None:
    """Populate *data* with BOM entries derived from the case hierarchy."""
    collection_name = root_obj.get("flight_case_collection", "")
    if not collection_name or collection_name not in bpy.data.collections:
        return

    col = bpy.data.collections[collection_name]
    all_objects = list(col.all_objects)

    # Count hardware
    hw_counts: dict[str, int] = {}
    for obj in all_objects:
        if obj.get("fc_type") == "hardware":
            hw_type = obj.get("hw_type", "unknown")
            hw_counts[hw_type] = hw_counts.get(hw_type, 0) + 1

    for hw_type, count in hw_counts.items():
        from ..hardware.hardware_library import HardwareLibrary
        hw_def = HardwareLibrary.get(hw_type)
        data.hardware_items.append({
            "name": hw_def.label if hw_def else hw_type,
            "count": count,
            "part_number": hw_def.part_number if hw_def else "",
            "manufacturer": hw_def.manufacturer if hw_def else "",
        })

    # Sum foam volumes
    foam_volumes: dict[str, float] = {}
    for obj in all_objects:
        if obj.get("fc_type") == "foam" and obj.data:
            bb = obj.bound_box
            w = max(v[0] for v in bb) - min(v[0] for v in bb)
            h = max(v[1] for v in bb) - min(v[1] for v in bb)
            d = max(v[2] for v in bb) - min(v[2] for v in bb)
            vol = w * h * d * 1_000_000_000  # m³ → mm³
            foam_type = root_obj.flight_case.foam.foam_type
            foam_volumes[foam_type] = foam_volumes.get(foam_type, 0) + vol

    for foam_type, volume_mm3 in foam_volumes.items():
        data.foam_items.append({
            "type": foam_type,
            "volume_mm3": round(volume_mm3, 1),
        })
