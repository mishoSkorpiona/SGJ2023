"""profiles/definitions/tongue_groove.py"""
from ..profile_library import ProfileDefinition


def TongueGrooveProfile() -> ProfileDefinition:
    t = 0.002
    l = 0.020
    tongue_w = 0.006
    tongue_h = 0.004

    cross_section = [
        (0,             0),
        (l,             0),
        (l,             t),
        (t + tongue_w,  t),
        (t + tongue_w,  t + tongue_h),
        (t,             t + tongue_h),
        (t,             l),
        (0,             l),
    ]
    return ProfileDefinition(
        name="TONGUE_GROOVE",
        label="Tongue & Groove",
        cut_angle=45.0,
        _cross_section=cross_section,
    )
