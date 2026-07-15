# SPDX-License-Identifier: GPL-3.0-or-later
"""
Flight Case Designer - Professional parametric flight case design add-on for Blender.

Generates complete, manufacturing-ready road/flight cases for the backline,
lighting, audio, and touring industries.  Fully parametric and non-destructive:
change any value and the case rebuilds automatically.
"""

bl_info = {
    "name": "Flight Case Designer",
    "author": "Flight Case Designer",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Flight Case",
    "description": (
        "Professional parametric flight case design tool. "
        "Generates manufacturing-ready cases with panels, profiles, hardware, "
        "foam, rivets, BOM and cut-list export."
    ),
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

# ---------------------------------------------------------------------------
# Lazy sub-module imports so Blender's reload mechanism works correctly.
# ---------------------------------------------------------------------------
if "bpy" in dir():
    import importlib
    from . import properties, operators
    from .ui import panels
    from . import exporters
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(exporters)

import bpy
from . import properties, operators
from .ui import panels


def register() -> None:
    properties.register()
    operators.register()
    panels.register()


def unregister() -> None:
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
