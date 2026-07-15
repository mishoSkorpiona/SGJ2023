"""profiles/definitions/corner_profile.py"""
from ..profile_library import ProfileDefinition


def CornerProfile() -> ProfileDefinition:
    t = 0.003
    l = 0.025

    # Corner profile: outer L-shape with inner lip.
    # The polygon is closed by the sweep helper — last vertex must not
    # duplicate the first vertex.
    cross_section = [
        (0,   0),
        (l,   0),
        (l,   t),
        (t,   t),
        (t,   l),
        (0,   l),
        (-t,  l),
        (-t,  -t),
        (l,   -t),
    ]
    return ProfileDefinition(
        name="CORNER",
        label="Corner Profile",
        cut_angle=45.0,
        _cross_section=cross_section,
    )
