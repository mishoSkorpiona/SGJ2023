# SPDX-License-Identifier: GPL-3.0-or-later
"""
Aluminium extrusion profile library.

Each entry describes one profile section.  The ``cross_section`` field is a
list of (x, y) coordinates (in metres) that define the closed 2-D outline.
This is used by :mod:`generators.profile_gen` to extrude the shape.

Adding new profiles
-------------------
Append a new dict to ``PROFILE_CATALOG``.  The cross-section origin should be
at (0, 0) and the profile should sit in the positive X / positive Y quadrant.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


ProfileSection = List[Tuple[float, float]]  # convenience alias


def _angle(size_mm: float, thickness_mm: float = 3.0) -> ProfileSection:
    """L-shaped angle. *size_mm* = leg length, *thickness_mm* = wall thickness."""
    s = size_mm / 1000.0
    t = thickness_mm / 1000.0
    return [(0, 0), (s, 0), (s, t), (t, t), (t, s), (0, s)]


def _double_angle(size_mm: float, thickness_mm: float = 3.0) -> ProfileSection:
    """T-shaped double angle."""
    s = size_mm / 1000.0
    t = thickness_mm / 1000.0
    half = s / 2.0
    ht   = t / 2.0
    return [
        (0, 0), (s, 0), (s, t),
        (half + ht, t), (half + ht, s), (half - ht, s),
        (half - ht, t), (0, t),
    ]


def _h_profile(size_mm: float, thickness_mm: float = 3.0) -> ProfileSection:
    """H cross-section."""
    s = size_mm / 1000.0
    t = thickness_mm / 1000.0
    half = s / 2.0
    ht   = t / 2.0
    return [
        (0, 0), (s, 0), (s, t),
        (half + ht, t), (half + ht, s - t), (s, s - t), (s, s), (0, s),
        (0, s - t), (half - ht, s - t), (half - ht, t), (0, t),
    ]


def _lid_profile(size_mm: float, thickness_mm: float = 3.0) -> ProfileSection:
    """
    Lid extrusion: two flanges with a central tongue.
    Used at the body/lid seam to create a weather-tight closure.
    """
    s = size_mm / 1000.0
    t = thickness_mm / 1000.0
    tongue_h = s * 0.4
    return [
        (0, 0), (s, 0), (s, t),
        (s * 0.6 + t, t), (s * 0.6 + t, t + tongue_h),
        (s * 0.6 - t, t + tongue_h), (s * 0.6 - t, t),
        (t, t), (t, s * 0.8), (0, s * 0.8),
    ]


def _corner_profile(size_mm: float, thickness_mm: float = 3.0) -> ProfileSection:
    """Corner trim extrusion (right-angle bracket)."""
    return _angle(size_mm, thickness_mm)


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

PROFILE_CATALOG: List[Dict[str, Any]] = [
    {
        "id":             "angle_20x3",
        "type":           "ANGLE",
        "name":           "Angle 20×3 mm",
        "size_mm":        20.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.190,
        "cross_section":  _angle(20.0, 3.0),
        "notes":          "Light-duty angle for small cases.",
    },
    {
        "id":             "angle_30x3",
        "type":           "ANGLE",
        "name":           "Angle 30×3 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.290,
        "cross_section":  _angle(30.0, 3.0),
        "notes":          "Standard flight case angle.",
    },
    {
        "id":             "angle_40x3",
        "type":           "ANGLE",
        "name":           "Angle 40×3 mm",
        "size_mm":        40.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.390,
        "cross_section":  _angle(40.0, 3.0),
        "notes":          "Heavy-duty angle for large road cases.",
    },
    {
        "id":             "double_angle_30x3",
        "type":           "DOUBLE_ANGLE",
        "name":           "Double Angle 30×3 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.420,
        "cross_section":  _double_angle(30.0, 3.0),
        "notes":          "Double-angle for intermediate panel joints.",
    },
    {
        "id":             "tongue_groove_30",
        "type":           "TONGUE_GROOVE",
        "name":           "Tongue & Groove 30 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.350,
        "cross_section":  _lid_profile(30.0, 3.0),
        "notes":          "Tongue and groove for panel interlocking.",
    },
    {
        "id":             "lid_profile_30",
        "type":           "LID_PROFILE",
        "name":           "Lid Profile 30 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.380,
        "cross_section":  _lid_profile(30.0, 3.0),
        "notes":          "Seam profile with central tongue for lid closure.",
    },
    {
        "id":             "h_profile_30",
        "type":           "H_PROFILE",
        "name":           "H Profile 30 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.410,
        "cross_section":  _h_profile(30.0, 3.0),
        "notes":          "H-section for structural panel joiners.",
    },
    {
        "id":             "corner_profile_30",
        "type":           "CORNER_PROFILE",
        "name":           "Corner Profile 30 mm",
        "size_mm":        30.0,
        "thickness_mm":   3.0,
        "material":       "Aluminium 6061-T6",
        "weight_per_m_kg":0.290,
        "cross_section":  _corner_profile(30.0, 3.0),
        "notes":          "Right-angle corner bracket extrusion.",
    },
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_profile_def(profile_id: str) -> Optional[Dict[str, Any]]:
    """Return the catalog entry whose ``id`` matches *profile_id*, or ``None``."""
    for entry in PROFILE_CATALOG:
        if entry["id"] == profile_id:
            return entry
    return None


def get_profiles_by_type(profile_type: str) -> List[Dict[str, Any]]:
    """Return all catalog entries whose ``type`` matches *profile_type*."""
    return [e for e in PROFILE_CATALOG if e["type"] == profile_type]


def get_profile_cross_section(profile_id: str) -> Optional[ProfileSection]:
    """Return the 2-D cross-section for *profile_id*, or ``None`` if not found."""
    entry = get_profile_def(profile_id)
    return entry["cross_section"] if entry else None
