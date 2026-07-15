"""templates/lift_off_lid.py"""
from __future__ import annotations
import bpy
from .base_template import BaseTemplate


class LiftOffLidTemplate(BaseTemplate):
    """Detachable (lift-off) lid case."""

    label = "Lift-off Lid"

    def build_geometry(self, root_obj, params, context):
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.30, has_lid=True)
        self._run_profile_generator(root_obj, params, context)
        self._run_foam_generator(root_obj, params, context)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
