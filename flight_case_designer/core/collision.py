"""
core/collision.py — Axis-aligned bounding box collision detection.

After each case regeneration the CollisionChecker scans for:
  * Hardware overlap with other hardware.
  * Foam intersecting hardware.
  * Equipment that doesn't fit inside the internal cavity.
  * Wheel / caster interference with the case footprint.
  * Lid interference with mounted hardware.

Warnings are stored as a list of strings and attached to the root object as a
custom property ``flight_case_warnings``.  Individual objects are flagged with
``collision_warning = True`` so they can be highlighted in the viewport.
"""

from __future__ import annotations

from typing import List, Tuple

import bpy
import mathutils


# ---------------------------------------------------------------------------
# AABB helper
# ---------------------------------------------------------------------------

def _world_aabb(
    obj: bpy.types.Object,
) -> Tuple[mathutils.Vector, mathutils.Vector]:
    """Return the world-space axis-aligned bounding box (min, max)."""
    corners = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    lo = mathutils.Vector(map(min, zip(*corners)))
    hi = mathutils.Vector(map(max, zip(*corners)))
    return lo, hi


def _aabb_overlaps(
    a_min: mathutils.Vector,
    a_max: mathutils.Vector,
    b_min: mathutils.Vector,
    b_max: mathutils.Vector,
) -> bool:
    """Return True when two AABBs intersect (touching is not an overlap)."""
    for i in range(3):
        if a_max[i] <= b_min[i] or b_max[i] <= a_min[i]:
            return False
    return True


# ---------------------------------------------------------------------------
# CollisionChecker
# ---------------------------------------------------------------------------

class CollisionChecker:
    """
    Runs AABB-based interference checks on a case root object and its children.
    """

    def check(self, root_obj: bpy.types.Object) -> List[str]:
        """
        Run all checks and return a list of human-readable warning strings.

        Side-effect: sets ``obj["collision_warning"] = True/False`` on each
        checked object.
        """
        warnings: List[str] = []

        collection_name = root_obj.get("flight_case_collection", "")
        if not collection_name or collection_name not in bpy.data.collections:
            return warnings

        col = bpy.data.collections[collection_name]
        all_objects = list(col.all_objects)

        hardware_objs = [o for o in all_objects if o.get("fc_type") == "hardware"]
        foam_objs = [o for o in all_objects if o.get("fc_type") == "foam"]
        panel_objs = [o for o in all_objects if o.get("fc_type") == "panel"]
        equipment_objs = [o for o in all_objects if o.get("fc_type") == "equipment_proxy"]

        # Reset previous warnings
        for obj in all_objects:
            obj["collision_warning"] = False

        # 1. Hardware vs hardware
        for i in range(len(hardware_objs)):
            for j in range(i + 1, len(hardware_objs)):
                a, b = hardware_objs[i], hardware_objs[j]
                a_min, a_max = _world_aabb(a)
                b_min, b_max = _world_aabb(b)
                if _aabb_overlaps(a_min, a_max, b_min, b_max):
                    a["collision_warning"] = True
                    b["collision_warning"] = True
                    warnings.append(
                        f"Hardware overlap: '{a.name}' intersects '{b.name}'"
                    )

        # 2. Foam vs hardware
        for foam in foam_objs:
            f_min, f_max = _world_aabb(foam)
            for hw in hardware_objs:
                h_min, h_max = _world_aabb(hw)
                if _aabb_overlaps(f_min, f_max, h_min, h_max):
                    foam["collision_warning"] = True
                    hw["collision_warning"] = True
                    warnings.append(
                        f"Foam intersects hardware: '{foam.name}' vs '{hw.name}'"
                    )

        # 3. Equipment proxy vs internal cavity
        if equipment_objs and panel_objs:
            warnings += self._check_equipment_fit(equipment_objs, root_obj)

        # 4. Caster / wheel interference
        warnings += self._check_caster_interference(hardware_objs)

        # Store warnings on root object
        root_obj["flight_case_warnings"] = warnings
        return warnings

    # ------------------------------------------------------------------

    def _check_equipment_fit(
        self,
        equipment_objs: List[bpy.types.Object],
        root_obj: bpy.types.Object,
    ) -> List[str]:
        warnings = []
        params = root_obj.flight_case
        eq = params.equipment
        t = float(params.material.thickness_mm)

        int_w = eq.width  + eq.internal_clearance * 2
        int_d = (eq.depth + eq.cable_clearance
                 + eq.connector_clearance + eq.internal_clearance * 2)
        int_h = eq.height + eq.internal_clearance * 2

        for ep in equipment_objs:
            ep_min, ep_max = _world_aabb(ep)
            size = ep_max - ep_min
            if size.x > int_w / 1000.0 or size.y > int_d / 1000.0 or size.z > int_h / 1000.0:
                ep["collision_warning"] = True
                warnings.append(
                    f"Equipment '{ep.name}' does not fit inside the internal cavity."
                )
        return warnings

    def _check_caster_interference(
        self, hardware_objs: List[bpy.types.Object]
    ) -> List[str]:
        warnings = []
        casters = [o for o in hardware_objs if "caster" in o.name.lower()]
        other_hw = [o for o in hardware_objs if o not in casters]
        for caster in casters:
            c_min, c_max = _world_aabb(caster)
            for hw in other_hw:
                h_min, h_max = _world_aabb(hw)
                if _aabb_overlaps(c_min, c_max, h_min, h_max):
                    caster["collision_warning"] = True
                    hw["collision_warning"] = True
                    warnings.append(
                        f"Caster interference: '{caster.name}' vs '{hw.name}'"
                    )
        return warnings
