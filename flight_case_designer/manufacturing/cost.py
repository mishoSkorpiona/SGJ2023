"""
manufacturing/cost.py — Cost estimator (stub).

Prices are unit-agnostic.  This module is designed to be extended once a
supplier database / price list is available.

Default unit prices (per unit / per metre / per kg) can be overridden by
loading a JSON price file.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


# Default prices (arbitrary currency units)
DEFAULT_PRICES: dict[str, float] = {
    # Plywood — per m²
    "plywood_per_m2": 25.0,
    # Aluminium profile — per metre
    "profile_per_m": 4.50,
    # Foam — per litre
    "foam_per_litre": 2.00,
    # Hardware items — flat rate each
    "butterfly_latch": 3.50,
    "spring_handle": 6.00,
    "ball_corner": 1.80,
    "cast_corner": 2.50,
    "hinge": 2.00,
    "rubber_foot": 0.80,
    "caster": 8.00,
    "rack_rail": 15.00,
}

_prices: dict[str, float] = dict(DEFAULT_PRICES)


def load_price_list(filepath: str) -> None:
    """Load custom prices from a JSON file."""
    global _prices
    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _prices.update(data)


def estimate_cost(data: "CaseData") -> float:
    """
    Return a rough total cost estimate from *data*.

    Updates data.total_cost in place and also returns the value.
    """
    cost = 0.0

    # Panels
    for panel in data.panels:
        area_m2 = (panel["width_mm"] / 1000) * (panel["height_mm"] / 1000)
        cost += area_m2 * _prices.get("plywood_per_m2", 25.0) * panel.get("qty", 1)

    # Profile cuts
    for cut in data.profile_cuts:
        length_m = cut["length_mm"] / 1000
        cost += length_m * _prices.get("profile_per_m", 4.50) * cut.get("qty", 1)

    # Foam
    for foam in data.foam_items:
        volume_litres = foam["volume_mm3"] / 1_000_000
        cost += volume_litres * _prices.get("foam_per_litre", 2.00)

    # Hardware
    for hw in data.hardware_items:
        unit_price = _prices.get(hw["name"].lower().replace(" ", "_"), 3.00)
        cost += unit_price * hw["count"]

    data.total_cost = round(cost, 2)
    return data.total_cost
