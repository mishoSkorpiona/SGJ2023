"""templates/cable_doghouse.py"""
from .base_template import BaseTemplate


class CableDoghouse(BaseTemplate):
    label = "Cable Doghouse"

    def build_geometry(self, root_obj, params, context):
        params.foam.cable_channels = True
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.35, has_lid=True)
        self._run_profile_generator(root_obj, params, context)
        self._run_foam_generator(root_obj, params, context)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
