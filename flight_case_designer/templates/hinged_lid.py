"""templates/hinged_lid.py"""
from __future__ import annotations
from .base_template import BaseTemplate


class HingedLidTemplate(BaseTemplate):
    """Hinged lid case — hinges placed on back edge, latches on front."""

    label = "Hinged Lid"

    def build_geometry(self, root_obj, params, context):
        # Force hinges on
        params.hardware.hinges = True
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.40, has_lid=True)
        self._run_profile_generator(root_obj, params, context)
        self._run_foam_generator(root_obj, params, context)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
