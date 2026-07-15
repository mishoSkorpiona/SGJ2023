"""
templates/base_template.py — Abstract base class for all case templates.

Every template must implement ``build_geometry`` which receives the root empty
object, the current CaseSettings, and the Blender context.  It should call
the appropriate geometry generators and hardware placer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.parameters import CaseSettings


class BaseTemplate(ABC):
    """
    Abstract base for flight case templates.

    Subclasses override ``build_geometry`` to define:
      * Which panels to generate (lid height fraction, whether lid exists).
      * Which profiles to apply.
      * Which hardware to place (overrides to HardwareSettings allowed).
      * Whether rack supports / dividers / shelves are added.
      * Foam configuration.
    """

    # Human-readable name used in UI listings
    label: str = "Base Template"

    @abstractmethod
    def build_geometry(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
    ) -> None:
        """
        Build or rebuild all geometry for this case type.

        Parameters
        ----------
        root_obj:
            The flight case root empty object (parent of all sub-objects).
        params:
            The active ``CaseSettings`` property group attached to *root_obj*.
        context:
            The current Blender context.
        """

    # ------------------------------------------------------------------
    # Convenience helpers shared by all templates
    # ------------------------------------------------------------------

    def _run_panel_generator(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
        lid_height_fraction: float = 0.35,
        has_lid: bool = True,
    ) -> None:
        if params.panels_dirty:
            from ..geometry.panel_generator import generate_panels
            generate_panels(root_obj, params, context, lid_height_fraction, has_lid)

    def _run_profile_generator(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
    ) -> None:
        if params.panels_dirty:
            from ..geometry.profile_generator import generate_profiles
            generate_profiles(root_obj, params, context)

    def _run_foam_generator(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
    ) -> None:
        if params.foam_dirty:
            from ..geometry.foam_generator import generate_foam
            generate_foam(root_obj, params, context)

    def _run_hardware_placer(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
    ) -> None:
        if params.hardware_dirty:
            from ..hardware.hardware_placer import place_hardware
            place_hardware(root_obj, params, context)

    def _run_rivet_generator(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
    ) -> None:
        if params.hardware_dirty:
            from ..geometry.rivet_generator import generate_rivets
            generate_rivets(root_obj, params, context)

    def _run_support_generator(
        self,
        root_obj: bpy.types.Object,
        params: "CaseSettings",
        context: bpy.types.Context,
        **kwargs,
    ) -> None:
        from ..geometry.support_generator import generate_supports
        generate_supports(root_obj, params, context, **kwargs)
