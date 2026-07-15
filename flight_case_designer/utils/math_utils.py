"""
utils/math_utils.py — Vector helpers and geometric utilities.
"""

from __future__ import annotations

import math
from typing import Tuple

import mathutils


def mm_to_m(value_mm: float) -> float:
    """Convert millimetres to metres (Blender's native unit)."""
    return value_mm / 1000.0


def m_to_mm(value_m: float) -> float:
    """Convert metres to millimetres."""
    return value_m * 1000.0


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to the range [lo, hi]."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between *a* and *b* by factor *t*."""
    return a + (b - a) * t


def distribute_evenly(
    length: float,
    spacing: float,
    edge_offset: float,
) -> list[float]:
    """
    Return a list of positions along *length* (starting at 0) evenly
    distributed with the given *spacing* and *edge_offset*.

    The first and last positions are at *edge_offset* from each end.
    """
    usable = length - 2.0 * edge_offset
    if usable <= 0:
        return [length / 2.0]
    count = max(1, round(usable / spacing) + 1)
    if count == 1:
        return [length / 2.0]
    step = usable / (count - 1)
    return [edge_offset + i * step for i in range(count)]


def rotate_point_2d(
    x: float, y: float, angle_rad: float
) -> Tuple[float, float]:
    """Rotate a 2-D point around the origin."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return c * x - s * y, s * x + c * y


def bounding_box_center(
    points: list[mathutils.Vector],
) -> mathutils.Vector:
    """Return the centre of the axis-aligned bounding box of *points*."""
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]
    return mathutils.Vector(
        ((min(xs) + max(xs)) / 2,
         (min(ys) + max(ys)) / 2,
         (min(zs) + max(zs)) / 2)
    )


def rack_unit_height(units: int) -> float:
    """Return the height in mm for a given number of rack units."""
    return units * 44.45
