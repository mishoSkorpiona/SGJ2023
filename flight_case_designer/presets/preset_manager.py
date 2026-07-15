"""
presets/preset_manager.py — Save/load JSON presets for CaseSettings.

A preset is a JSON file containing a snapshot of a CaseSettings property
group.  Presets can be saved to / loaded from:
  * The add-on's built-in ``defaults/`` folder (read-only).
  * A user-specified directory.

The PresetManager exposes class methods callable from Blender operators.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import bpy


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _pg_to_dict(pg: bpy.types.PropertyGroup) -> Dict[str, Any]:
    """Recursively serialise a PropertyGroup to a plain dict."""
    result: Dict[str, Any] = {}
    for prop_name in pg.bl_rna.properties.keys():
        if prop_name in ("name", "rna_type"):
            continue
        value = getattr(pg, prop_name)
        if isinstance(value, bpy.types.PropertyGroup):
            result[prop_name] = _pg_to_dict(value)
        elif hasattr(value, "__iter__") and not isinstance(value, str):
            result[prop_name] = list(value)
        else:
            result[prop_name] = value
    return result


def _dict_to_pg(data: Dict[str, Any], pg: bpy.types.PropertyGroup) -> None:
    """Recursively apply a plain dict onto a PropertyGroup."""
    for key, value in data.items():
        if not hasattr(pg, key):
            continue
        attr = getattr(pg, key)
        if isinstance(attr, bpy.types.PropertyGroup):
            _dict_to_pg(value, attr)
        else:
            try:
                setattr(pg, key, value)
            except (TypeError, AttributeError):
                pass


# ---------------------------------------------------------------------------
# PresetManager
# ---------------------------------------------------------------------------

class PresetManager:
    """
    Manages serialisation and discovery of flight case presets.

    All presets are stored as JSON files.
    """

    BUILTIN_DIR = os.path.join(os.path.dirname(__file__), "defaults")

    @classmethod
    def save(cls, filepath: str, root_obj: bpy.types.Object) -> None:
        """Save the current case settings to *filepath*."""
        params = root_obj.flight_case
        data = _pg_to_dict(params)
        data["_preset_format"] = 1
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        print(f"Preset saved to {filepath}")

    @classmethod
    def load(cls, filepath: str, root_obj: bpy.types.Object) -> None:
        """Load a preset from *filepath* onto *root_obj*."""
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        data.pop("_preset_format", None)
        _dict_to_pg(data, root_obj.flight_case)
        # Trigger a full rebuild
        root_obj.flight_case.panels_dirty = True
        root_obj.flight_case.hardware_dirty = True
        root_obj.flight_case.foam_dirty = True
        print(f"Preset loaded from {filepath}")

    @classmethod
    def list_builtins(cls) -> List[str]:
        """Return a list of paths to built-in preset files."""
        if not os.path.isdir(cls.BUILTIN_DIR):
            return []
        return [
            os.path.join(cls.BUILTIN_DIR, f)
            for f in os.listdir(cls.BUILTIN_DIR)
            if f.endswith(".json")
        ]

    @classmethod
    def list_user(cls, directory: str) -> List[str]:
        """Return preset files in a user-specified directory."""
        if not os.path.isdir(directory):
            return []
        return [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".json")
        ]
