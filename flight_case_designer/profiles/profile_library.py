"""
profiles/profile_library.py — Registry of aluminium extrusion profiles.

A profile definition provides:
  * cross_section_2d() → list of (u, v) tuples (metres)
  * offset_rules       → dict of placement offsets
  * cut_angle          → mitre angle (degrees)
  * material           → e.g. "6063-T5 Aluminium"

New profiles can be registered at runtime via ProfileLibrary.register().
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .definitions.angle import AngleProfile
from .definitions.double_angle import DoubleAngleProfile
from .definitions.tongue_groove import TongueGrooveProfile
from .definitions.lid_profile import LidProfile
from .definitions.h_profile import HProfile
from .definitions.corner_profile import CornerProfile


@dataclass
class ProfileDefinition:
    """Data class describing a single aluminium extrusion profile."""

    name: str
    label: str
    material: str = "6063-T5 Aluminium"
    cut_angle: float = 45.0  # degrees
    # Callable or static cross-section data
    _cross_section: List[Tuple[float, float]] = field(default_factory=list, repr=False)

    def cross_section_2d(self) -> List[Tuple[float, float]]:
        """Return the 2-D cross-section as (u, v) tuples in metres."""
        return list(self._cross_section)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "material": self.material,
            "cut_angle": self.cut_angle,
            "cross_section": self._cross_section,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileDefinition":
        return cls(
            name=data["name"],
            label=data.get("label", data["name"]),
            material=data.get("material", "Aluminium"),
            cut_angle=data.get("cut_angle", 45.0),
            _cross_section=[tuple(p) for p in data.get("cross_section", [])],
        )


class ProfileLibrary:
    """
    Singleton-style registry for profile definitions.

    Built-in profiles are loaded at import time.  User-defined profiles can be
    added via ``register()`` or ``load_from_json()``.
    """

    _profiles: Dict[str, ProfileDefinition] = {}

    @classmethod
    def _init_builtins(cls) -> None:
        builtins = [
            AngleProfile(),
            DoubleAngleProfile(),
            TongueGrooveProfile(),
            LidProfile(),
            HProfile(),
            CornerProfile(),
        ]
        for p in builtins:
            cls._profiles[p.name] = p

    @classmethod
    def get(cls, name: str) -> Optional[ProfileDefinition]:
        """Return the profile definition for *name*, or None."""
        if not cls._profiles:
            cls._init_builtins()
        return cls._profiles.get(name)

    @classmethod
    def all_names(cls) -> List[str]:
        if not cls._profiles:
            cls._init_builtins()
        return list(cls._profiles.keys())

    @classmethod
    def register(cls, definition: ProfileDefinition) -> None:
        """Add or replace a profile in the registry."""
        cls._profiles[definition.name] = definition

    @classmethod
    def load_from_json(cls, filepath: str) -> None:
        """Load profile definitions from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        profiles = data if isinstance(data, list) else data.get("profiles", [])
        for item in profiles:
            cls.register(ProfileDefinition.from_dict(item))

    @classmethod
    def save_to_json(cls, filepath: str) -> None:
        """Serialise all registered profiles to a JSON file."""
        data = [p.to_dict() for p in cls._profiles.values()]
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)


# Initialise built-ins on first import
ProfileLibrary._init_builtins()
