"""profiles/definitions/angle.py — L-angle extrusion cross-section."""
from ..profile_library import ProfileDefinition


def AngleProfile() -> ProfileDefinition:
    """
    Simple L-angle: two flanges at 90 degrees.
    Cross-section in metres (2 mm flange, 20 mm leg).
    """
    t = 0.002  # 2 mm thickness
    l = 0.020  # 20 mm leg

    cross_section = [
        (0,   0),
        (l,   0),
        (l,   t),
        (t,   t),
        (t,   l),
        (0,   l),
    ]
    return ProfileDefinition(
        name="ANGLE",
        label="Angle",
        cut_angle=45.0,
        _cross_section=cross_section,
    )
