"""templates/mixer_case.py"""
from .base_template import BaseTemplate


class MixerCase(BaseTemplate):
    label = "Mixer Case"

    def build_geometry(self, root_obj, params, context):
        params.hardware.butterfly_latches = True
        params.hardware.spring_handles = True
        # Mixers often have angled front — use a deeper lid fraction
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.5, has_lid=True)
        self._run_profile_generator(root_obj, params, context)
        self._run_foam_generator(root_obj, params, context)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
