"""profiles/definitions/h_profile.py"""
from ..profile_library import ProfileDefinition


def HProfile() -> ProfileDefinition:
    t = 0.002
    l = 0.018

    cross_section = [
        (0,   0),
        (t,   0),
        (t,   l / 2 - t / 2),
        (l - t, l / 2 - t / 2),
        (l - t, 0),
        (l,   0),
        (l,   l),
        (l - t, l),
        (l - t, l / 2 + t / 2),
        (t,   l / 2 + t / 2),
        (t,   l),
        (0,   l),
    ]
    return ProfileDefinition(
        name="H_PROFILE",
        label="H Profile",
        cut_angle=90.0,
        _cross_section=cross_section,
    )
