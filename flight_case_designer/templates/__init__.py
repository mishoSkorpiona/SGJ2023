"""templates/__init__.py — Template registry."""

from __future__ import annotations

from .base_template import BaseTemplate
from .lift_off_lid import LiftOffLidTemplate
from .hinged_lid import HingedLidTemplate
from .rack_case import RackCaseTemplate
from .trunk import TrunkTemplate
from .cable_doghouse import CableDoghouse
from .drawer_case import DrawerCase
from .speaker_case import SpeakerCase
from .amplifier_case import AmplifierCase
from .mixer_case import MixerCase
from .keyboard_case import KeyboardCase
from .custom_box import CustomBox


# Maps CaseSettings.case_type enum identifiers → template class.
# The enum keys use SCREAMING_SNAKE_CASE to match Blender's EnumProperty
# convention; template classes use CamelCase + "Template" suffix.
_REGISTRY: dict[str, type[BaseTemplate]] = {
    "LIFT_OFF_LID":   LiftOffLidTemplate,
    "HINGED_LID":     HingedLidTemplate,
    "RACK_CASE":      RackCaseTemplate,
    "TRUNK":          TrunkTemplate,
    "CABLE_DOGHOUSE": CableDoghouse,
    "DRAWER_CASE":    DrawerCase,
    "SPEAKER_CASE":   SpeakerCase,
    "AMPLIFIER_CASE": AmplifierCase,
    "MIXER_CASE":     MixerCase,
    "KEYBOARD_CASE":  KeyboardCase,
    "CUSTOM_BOX":     CustomBox,
}


def get_template(case_type: str) -> type[BaseTemplate]:
    """Return the template class for the given *case_type* identifier."""
    cls = _REGISTRY.get(case_type)
    if cls is None:
        raise KeyError(f"Unknown case type: {case_type!r}")
    return cls


def register() -> None:
    pass


def unregister() -> None:
    pass
