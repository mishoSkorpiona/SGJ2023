"""profiles/definitions/double_angle.py — Double L-angle cross-section."""
from ..profile_library import ProfileDefinition


def DoubleAngleProfile() -> ProfileDefinition:
    t = 0.002
    l = 0.020

    cross_section = [
        (0,    0),
        (l,    0),
        (l,    t),
        (t,    t),
        (t,    l),
        (0,    l),
        (0,    l + t),
        (-t,   l + t),
        (-t,   0),
    ]
    return ProfileDefinition(
        name="DOUBLE_ANGLE",
        label="Double Angle",
        cut_angle=45.0,
        _cross_section=cross_section,
    )
