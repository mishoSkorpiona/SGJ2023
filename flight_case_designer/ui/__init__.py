"""ui/__init__.py"""

from . import operators
from . import sidebar
from .panels import (
    project_panel,
    equipment_panel,
    case_panel,
    profiles_panel,
    hardware_panel,
    foam_panel,
    panels_panel,
    manufacturing_panel,
    export_panel,
)

_PANEL_MODULES = [
    project_panel,
    equipment_panel,
    case_panel,
    profiles_panel,
    hardware_panel,
    foam_panel,
    panels_panel,
    manufacturing_panel,
    export_panel,
]


def register() -> None:
    operators.register()
    for mod in _PANEL_MODULES:
        mod.register()


def unregister() -> None:
    for mod in reversed(_PANEL_MODULES):
        mod.unregister()
    operators.unregister()
