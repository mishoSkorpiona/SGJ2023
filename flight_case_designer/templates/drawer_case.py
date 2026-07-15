"""templates/drawer_case.py"""
from .base_template import BaseTemplate


class DrawerCase(BaseTemplate):
    label = "Drawer Case"

    def build_geometry(self, root_obj, params, context):
        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.0, has_lid=False)
        self._run_profile_generator(root_obj, params, context)
        # Drawer dividers at mid-height
        self._run_support_generator(root_obj, params, context,
                                    add_shelves=True)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
