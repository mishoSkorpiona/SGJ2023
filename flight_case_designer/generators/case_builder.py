# SPDX-License-Identifier: GPL-3.0-or-later
"""
CaseDimensions – the central dimensional model.

All generators receive a single ``CaseDimensions`` instance so that every
component is derived from the same parametric calculation.  All values are
stored internally in **metres** (Blender's native unit).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties import FCD_SceneProperties

# 1U rack height (EIA-310)
_RACK_U_HEIGHT = 0.04445  # metres


class CaseDimensions:
    """
    Compute all derived dimensions from the scene property groups.

    Attributes (all in metres unless noted)
    ----------------------------------------
    eq_w / eq_d / eq_h     Equipment external dimensions.
    eq_weight              Equipment weight in kg.
    foam_t/b/l/r/f/ba      Foam thickness per face (top/bottom/left/right/front/back).
    int_w / int_d / int_h  Internal cavity (inside plywood walls).
    ext_w / ext_d / ext_h  External case dimensions.
    ply_t                  Plywood thickness.
    body_h / lid_h         Body and lid heights (for split cases).
    prof_t                 Aluminium profile nominal size (mm expressed as m).
    split_z                Z-coordinate of the body/lid interface seam.
    case_type              String identifier, e.g. ``"LIFTOFF_LID"``.
    """

    def __init__(self, props: "FCD_SceneProperties") -> None:
        eq   = props.equipment
        case = props.case
        hdw  = props.hardware

        # ------------------------------------------------------------------ #
        # Plywood thickness
        # ------------------------------------------------------------------ #
        if case.ply_thickness_preset == "CUSTOM":
            self.ply_t = case.ply_thickness_custom / 1000.0
        else:
            self.ply_t = float(case.ply_thickness_preset) / 1000.0

        # ------------------------------------------------------------------ #
        # Equipment dimensions
        # ------------------------------------------------------------------ #
        self.eq_w      = eq.equipment_width  / 1000.0
        self.eq_d      = eq.equipment_depth  / 1000.0
        self.eq_h      = eq.equipment_height / 1000.0
        self.eq_weight = eq.equipment_weight

        # ------------------------------------------------------------------ #
        # Foam (apply compression factor)
        # ------------------------------------------------------------------ #
        comp = 1.0 - (eq.foam_compression / 100.0)
        if eq.asymmetric_foam:
            self.foam_t  = eq.foam_top    / 1000.0 * comp
            self.foam_b  = eq.foam_bottom / 1000.0 * comp
            self.foam_l  = eq.foam_left   / 1000.0 * comp
            self.foam_r  = eq.foam_right  / 1000.0 * comp
            self.foam_f  = eq.foam_front  / 1000.0 * comp
            self.foam_ba = eq.foam_back   / 1000.0 * comp
        else:
            # Symmetric: use foam_top / foam_bottom for vertical,
            # foam_left for all four sides.
            self.foam_t  = eq.foam_top    / 1000.0 * comp
            self.foam_b  = eq.foam_bottom / 1000.0 * comp
            side         = eq.foam_left   / 1000.0 * comp
            self.foam_l  = side
            self.foam_r  = side
            self.foam_f  = side
            self.foam_ba = side

        # ------------------------------------------------------------------ #
        # Internal cavity
        # ------------------------------------------------------------------ #
        ic = eq.internal_clearance / 1000.0
        ag = eq.air_gap            / 1000.0
        extra = 2.0 * (ic + ag)

        self.int_w = self.eq_w + self.foam_l  + self.foam_r  + extra
        self.int_d = self.eq_d + self.foam_f  + self.foam_ba + extra
        self.int_h = self.eq_h + self.foam_t  + self.foam_b  + extra

        # ------------------------------------------------------------------ #
        # Override for rack case (EIA-310 standard)
        # ------------------------------------------------------------------ #
        self.case_type = case.case_type
        if case.case_type == "RACK_CASE":
            self.int_w = 0.4826          # 19" = 482.6 mm internal rail width
            self.int_d = case.rack_depth / 1000.0
            self.int_h = case.rack_units * _RACK_U_HEIGHT + 0.010  # 10 mm margin

        # ------------------------------------------------------------------ #
        # External box
        # ------------------------------------------------------------------ #
        self.ext_w = self.int_w + 2.0 * self.ply_t
        self.ext_d = self.int_d + 2.0 * self.ply_t
        self.ext_h = self.int_h + 2.0 * self.ply_t

        # ------------------------------------------------------------------ #
        # Lid / body split
        # ------------------------------------------------------------------ #
        self.lid_ratio = case.lid_height_ratio
        self.lid_h     = self.ext_h * self.lid_ratio
        self.body_h    = self.ext_h - self.lid_h
        self.split_z   = self.body_h   # Z coordinate of the seam

        # ------------------------------------------------------------------ #
        # Profiles
        # ------------------------------------------------------------------ #
        self.prof_t        = case.profile_size / 1000.0
        self.profile_type  = case.profile_type

        # ------------------------------------------------------------------ #
        # Rivet parameters
        # ------------------------------------------------------------------ #
        self.rivet_spacing     = hdw.rivet_spacing     / 1000.0
        self.rivet_edge_offset = hdw.rivet_edge_offset / 1000.0
        self.rivet_diameter    = hdw.rivet_diameter    / 1000.0

        # ------------------------------------------------------------------ #
        # Weight estimate: plywood panels (rough)
        # ------------------------------------------------------------------ #
        density = {
            "BIRCH":          680.0,
            "PHENOLIC_BIRCH": 700.0,
            "MDF":            750.0,
        }.get(case.material_type, 680.0)

        panel_volume = self._panel_volume()
        self.ply_weight = panel_volume * density  # kg

    # ------------------------------------------------------------------ #
    # Helper: compute total plywood volume
    # ------------------------------------------------------------------ #

    def _panel_volume(self) -> float:
        """Return approximate total plywood volume in cubic metres."""
        t = self.ply_t
        w, d, h = self.ext_w, self.ext_d, self.ext_h
        # Six panels: top, bottom, front, back, left, right
        area = (
            2 * (w * d)                                # top + bottom
            + 2 * (w * h)                              # front + back (approx)
            + 2 * (d * h)                              # left + right (approx)
        )
        return area * t

    # ------------------------------------------------------------------ #
    # Convenience: returns the number of latches recommended
    # ------------------------------------------------------------------ #

    def auto_latch_count(self) -> int:
        """Return recommended latch count based on case width."""
        if self.ext_w < 0.5:
            return 2
        if self.ext_w < 0.9:
            return 3
        return 4

    def auto_handle_count(self) -> int:
        """Return recommended handle count per side based on weight."""
        if self.eq_weight <= 20:
            return 1
        return 2

    def total_weight(self) -> float:
        """Rough total case weight in kg."""
        foam_volume = (
            (self.foam_l + self.foam_r) * self.int_d * self.int_h
            + (self.foam_f + self.foam_ba) * self.int_w * self.int_h
            + (self.foam_t + self.foam_b) * self.int_w * self.int_d
        )
        foam_density = 30.0  # kg/m³ default
        foam_weight  = foam_volume * foam_density
        return self.eq_weight + self.ply_weight + foam_weight
