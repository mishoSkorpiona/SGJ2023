"""
Flight Case Designer — Blender Add-on
======================================
A professional parametric add-on for designing road/flight cases used by
backline, lighting, audio, and touring companies.

Compatible with Blender 4.x.
"""

bl_info = {
    "name": "Flight Case Designer",
    "author": "Flight Case Designer Contributors",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Flight Case",
    "description": (
        "Parametric flight case designer for manufacturing-ready "
        "road/flight cases used in the touring industry."
    ),
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy  # noqa: E402  (imported after bl_info)

# ---------------------------------------------------------------------------
# Sub-package imports — each sub-package exposes register() / unregister()
# ---------------------------------------------------------------------------
from . import core       # noqa: F401
from . import geometry   # noqa: F401
from . import hardware   # noqa: F401
from . import profiles   # noqa: F401
from . import templates  # noqa: F401
from . import manufacturing  # noqa: F401
from . import export     # noqa: F401
from . import drawings   # noqa: F401
from . import presets    # noqa: F401
from . import ui         # noqa: F401
from . import utils      # noqa: F401

# Ordered list of sub-modules that expose register/unregister
_MODULES = [
    utils,
    core,
    geometry,
    hardware,
    profiles,
    templates,
    manufacturing,
    export,
    drawings,
    presets,
    ui,
]


def register() -> None:
    """Register all add-on classes with Blender."""
    for mod in _MODULES:
        if hasattr(mod, "register"):
            mod.register()


def unregister() -> None:
    """Unregister all add-on classes from Blender."""
    for mod in reversed(_MODULES):
        if hasattr(mod, "unregister"):
            mod.unregister()
