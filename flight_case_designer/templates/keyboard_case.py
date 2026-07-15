"""templates/keyboard_case.py"""
from .base_template import BaseTemplate


class KeyboardCase(BaseTemplate):
    label = "Keyboard Case"

    def build_geometry(self, root_obj, params, context):
        params.hardware.butterfly_latches = True
        params.hardware.spring_handles = True
        params.foam.finger_pulls = True
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.25, has_lid=True)
        self._run_profile_generator(root_obj, params, context)
        self._run_foam_generator(root_obj, params, context)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
