"""profiles/definitions/lid_profile.py"""
from ..profile_library import ProfileDefinition


def LidProfile() -> ProfileDefinition:
    t = 0.002
    l = 0.016
    lip = 0.005

    cross_section = [
        (0,   0),
        (l,   0),
        (l,   t),
        (lip, t),
        (lip, t + lip),
        (0,   t + lip),
    ]
    return ProfileDefinition(
        name="LID",
        label="Lid Profile",
        cut_angle=45.0,
        _cross_section=cross_section,
    )
