"""
core/__init__.py — Flight Case Designer core sub-package.
"""

from . import parameters   # noqa: F401
from . import case_manager # noqa: F401
from . import collision    # noqa: F401


def register() -> None:
    parameters.register()


def unregister() -> None:
    parameters.unregister()
