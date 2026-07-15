# SPDX-License-Identifier: GPL-3.0-or-later
"""
Hardware catalog.

Each entry is a plain dict that describes one hardware item.  The dict keys
are used by the hardware generator to compute proxy geometry and by the BOM
exporter to produce part descriptions.

Adding new hardware
-------------------
Just append a new dict to ``HARDWARE_CATALOG``.  No other code changes are
needed – the exporter and future catalog UI will pick it up automatically.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Catalog entries
# ---------------------------------------------------------------------------
# Keys:
#   id          – unique string identifier
#   category    – grouping label for UI and BOM
#   name        – human-readable name
#   manufacturer– e.g. "Penn Elcom"
#   part_number – manufacturer part number
#   width_mm    – bounding box width  in mm
#   depth_mm    – bounding box depth  in mm
#   height_mm   – bounding box height in mm
#   weight_g    – weight per unit in grams
#   rivet_rows  – number of rivet rows
#   rivets_per_row – rivets per row
#   rivet_diameter_mm – standard rivet diameter
#   notes       – free-text notes

HARDWARE_CATALOG: List[Dict[str, Any]] = [

    # ------------------------------------------------------------------ #
    # Butterfly latches
    # ------------------------------------------------------------------ #
    {
        "id":              "butterfly_small",
        "category":        "Latch",
        "name":            "Butterfly Latch – Small",
        "manufacturer":    "Penn Elcom",
        "part_number":     "C1100",
        "width_mm":        53.0,
        "depth_mm":        12.0,
        "height_mm":       30.0,
        "weight_g":        80.0,
        "rivet_rows":      2,
        "rivets_per_row":  2,
        "rivet_diameter_mm": 4.8,
        "notes":           "Standard zinc-plated butterfly latch.",
    },
    {
        "id":              "butterfly_medium",
        "category":        "Latch",
        "name":            "Butterfly Latch – Medium",
        "manufacturer":    "Penn Elcom",
        "part_number":     "C1100EL",
        "width_mm":        60.0,
        "depth_mm":        12.0,
        "height_mm":       36.0,
        "weight_g":        100.0,
        "rivet_rows":      2,
        "rivets_per_row":  2,
        "rivet_diameter_mm": 4.8,
        "notes":           "Medium elongated butterfly latch.",
    },
    {
        "id":              "draw_latch",
        "category":        "Latch",
        "name":            "Draw Bolt Latch",
        "manufacturer":    "Penn Elcom",
        "part_number":     "C1103",
        "width_mm":        90.0,
        "depth_mm":        18.0,
        "height_mm":       25.0,
        "weight_g":        120.0,
        "rivet_rows":      2,
        "rivets_per_row":  3,
        "rivet_diameter_mm": 4.8,
        "notes":           "Heavy-duty draw-bolt latch with keeper.",
    },

    # ------------------------------------------------------------------ #
    # Handles
    # ------------------------------------------------------------------ #
    {
        "id":              "spring_handle_small",
        "category":        "Handle",
        "name":            "Spring Handle – Small (150 mm)",
        "manufacturer":    "Penn Elcom",
        "part_number":     "H1009",
        "width_mm":        150.0,
        "depth_mm":        50.0,
        "height_mm":       35.0,
        "weight_g":        200.0,
        "rivet_rows":      2,
        "rivets_per_row":  2,
        "rivet_diameter_mm": 4.8,
        "notes":           "Recessed spring-loaded side handle.",
    },
    {
        "id":              "spring_handle_large",
        "category":        "Handle",
        "name":            "Spring Handle – Large (200 mm)",
        "manufacturer":    "Penn Elcom",
        "part_number":     "H1010",
        "width_mm":        200.0,
        "depth_mm":        55.0,
        "height_mm":       40.0,
        "weight_g":        280.0,
        "rivet_rows":      2,
        "rivets_per_row":  3,
        "rivet_diameter_mm": 4.8,
        "notes":           "Large recessed spring handle for heavy cases.",
    },
    {
        "id":              "side_handle",
        "category":        "Handle",
        "name":            "Fixed Side Handle",
        "manufacturer":    "Penn Elcom",
        "part_number":     "H1013",
        "width_mm":        160.0,
        "depth_mm":        60.0,
        "height_mm":       30.0,
        "weight_g":        220.0,
        "rivet_rows":      2,
        "rivets_per_row":  2,
        "rivet_diameter_mm": 4.8,
        "notes":           "Rigid bolted side handle.",
    },

    # ------------------------------------------------------------------ #
    # Corners
    # ------------------------------------------------------------------ #
    {
        "id":              "ball_corner",
        "category":        "Corner",
        "name":            "Ball Corner (9-hole)",
        "manufacturer":    "Penn Elcom",
        "part_number":     "R2365Z",
        "width_mm":        38.0,
        "depth_mm":        38.0,
        "height_mm":       38.0,
        "weight_g":        55.0,
        "rivet_rows":      3,
        "rivets_per_row":  3,
        "rivet_diameter_mm": 4.8,
        "notes":           "Standard zinc 9-hole ball corner.",
    },
    {
        "id":              "cast_corner",
        "category":        "Corner",
        "name":            "Cast Recessed Corner",
        "manufacturer":    "Penn Elcom",
        "part_number":     "R2368",
        "width_mm":        50.0,
        "depth_mm":        50.0,
        "height_mm":       50.0,
        "weight_g":        150.0,
        "rivet_rows":      3,
        "rivets_per_row":  3,
        "rivet_diameter_mm": 4.8,
        "notes":           "Heavy-duty recessed cast corner for touring cases.",
    },

    # ------------------------------------------------------------------ #
    # Hinges
    # ------------------------------------------------------------------ #
    {
        "id":              "lid_hinge",
        "category":        "Hinge",
        "name":            "Lid Hinge",
        "manufacturer":    "Penn Elcom",
        "part_number":     "H1001",
        "width_mm":        60.0,
        "depth_mm":        6.0,
        "height_mm":       80.0,
        "weight_g":        90.0,
        "rivet_rows":      2,
        "rivets_per_row":  4,
        "rivet_diameter_mm": 4.8,
        "notes":           "Standard piano hinge section.",
    },

    # ------------------------------------------------------------------ #
    # Feet
    # ------------------------------------------------------------------ #
    {
        "id":              "rubber_foot",
        "category":        "Foot",
        "name":            "Rubber Foot (Ø36 mm)",
        "manufacturer":    "Generic",
        "part_number":     "RF-36",
        "width_mm":        36.0,
        "depth_mm":        36.0,
        "height_mm":       20.0,
        "weight_g":        20.0,
        "rivet_rows":      0,
        "rivets_per_row":  0,
        "rivet_diameter_mm": 0.0,
        "notes":           "Anti-slip rubber foot, screw-fit.",
    },

    # ------------------------------------------------------------------ #
    # Casters
    # ------------------------------------------------------------------ #
    {
        "id":              "caster_50mm",
        "category":        "Caster",
        "name":            "Swivel Caster 50 mm with brake",
        "manufacturer":    "Penn Elcom",
        "part_number":     "W0985",
        "width_mm":        70.0,
        "depth_mm":        70.0,
        "height_mm":       85.0,
        "weight_g":        250.0,
        "rivet_rows":      0,
        "rivets_per_row":  4,
        "rivet_diameter_mm": 6.4,
        "notes":           "50 mm swivel caster with top-lock brake.",
    },
    {
        "id":              "caster_75mm",
        "category":        "Caster",
        "name":            "Swivel Caster 75 mm with brake",
        "manufacturer":    "Penn Elcom",
        "part_number":     "W0986",
        "width_mm":        90.0,
        "depth_mm":        90.0,
        "height_mm":       110.0,
        "weight_g":        400.0,
        "rivet_rows":      0,
        "rivets_per_row":  4,
        "rivet_diameter_mm": 6.4,
        "notes":           "75 mm heavy-duty swivel caster.",
    },

    # ------------------------------------------------------------------ #
    # Rack rails
    # ------------------------------------------------------------------ #
    {
        "id":              "rack_rail_4u",
        "category":        "Rack Rail",
        "name":            "Rack Rail 4U",
        "manufacturer":    "Penn Elcom",
        "part_number":     "R0864/4",
        "width_mm":        15.0,
        "depth_mm":        6.0,
        "height_mm":       178.0,
        "weight_g":        180.0,
        "rivet_rows":      1,
        "rivets_per_row":  4,
        "rivet_diameter_mm": 4.8,
        "notes":           "4U steel rack rail, tapped M6.",
    },

    # ------------------------------------------------------------------ #
    # Stacking cups
    # ------------------------------------------------------------------ #
    {
        "id":              "stacking_cup",
        "category":        "Stacking",
        "name":            "Stacking Cup Ø50 mm",
        "manufacturer":    "Penn Elcom",
        "part_number":     "SC-50",
        "width_mm":        50.0,
        "depth_mm":        50.0,
        "height_mm":       15.0,
        "weight_g":        30.0,
        "rivet_rows":      1,
        "rivets_per_row":  4,
        "rivet_diameter_mm": 4.8,
        "notes":           "Steel stacking / anti-slip cup.",
    },

    # ------------------------------------------------------------------ #
    # Label holder
    # ------------------------------------------------------------------ #
    {
        "id":              "label_holder",
        "category":        "Label",
        "name":            "Label Holder 80 × 50 mm",
        "manufacturer":    "Penn Elcom",
        "part_number":     "LH-80",
        "width_mm":        80.0,
        "depth_mm":        3.0,
        "height_mm":       50.0,
        "weight_g":        15.0,
        "rivet_rows":      1,
        "rivets_per_row":  2,
        "rivet_diameter_mm": 4.8,
        "notes":           "Riveted aluminium label holder with clear window.",
    },
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_hardware_def(hw_id: str) -> Optional[Dict[str, Any]]:
    """Return the catalog entry whose ``id`` matches *hw_id*, or ``None``."""
    for entry in HARDWARE_CATALOG:
        if entry["id"] == hw_id:
            return entry
    return None


def get_hardware_by_category(category: str) -> List[Dict[str, Any]]:
    """Return all catalog entries that belong to *category*."""
    return [e for e in HARDWARE_CATALOG if e["category"] == category]
