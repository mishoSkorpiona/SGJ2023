"""templates/rack_case.py — 19-inch rack case template."""
from __future__ import annotations
from ..utils.math_utils import rack_unit_height
from .base_template import BaseTemplate


class RackCaseTemplate(BaseTemplate):
    """
    19-inch rack case.

    Equipment dimensions are overridden to match standard rack math:
      Width = 19" (482.6 mm) + side profiles
      Height = rack_units × 44.45 mm
    """

    label = "Rack Case (19\")"
    RACK_WIDTH_MM = 482.6

    def build_geometry(self, root_obj, params, context):
        # Enforce rack dimensions
        rack_units = params.rack_units
        params.equipment.width = self.RACK_WIDTH_MM
        params.equipment.height = rack_unit_height(rack_units)

        # Rack cases have no foam by default
        for side in ("top", "bottom", "front", "back", "left", "right"):
            setattr(params.foam, side, 0.0)

        # Force rack rails on
        params.hardware.rack_rails = True

        self._run_panel_generator(root_obj, params, context,
                                  lid_height_fraction=0.0, has_lid=False)
        self._run_profile_generator(root_obj, params, context)
        self._run_support_generator(root_obj, params, context,
                                    rack_units=rack_units)
        self._run_hardware_placer(root_obj, params, context)
        self._run_rivet_generator(root_obj, params, context)
