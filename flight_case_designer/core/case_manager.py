"""
core/case_manager.py — Top-level case creation and update orchestration.

The CaseManager is the central coordinator that:
1. Reads parameters from the active FlightCasePropertyGroup.
2. Selects and instantiates the appropriate case template.
3. Delegates to geometry generators in the correct order.
4. Manages the Blender collection hierarchy for each case.
5. Marks sub-systems dirty and triggers partial or full rebuilds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

import bpy

if TYPE_CHECKING:
    from .parameters import CaseSettings


# ---------------------------------------------------------------------------
# CaseData — decoupled snapshot used by exporters and manufacturing modules
# ---------------------------------------------------------------------------

@dataclass
class CaseData:
    """Serializable snapshot of a fully resolved case."""

    project_name: str = ""
    case_type: str = "LIFT_OFF_LID"

    # Resolved external dimensions (mm)
    ext_width: float = 0.0
    ext_depth: float = 0.0
    ext_height: float = 0.0

    # Resolved internal cavity dimensions (mm)
    int_width: float = 0.0
    int_depth: float = 0.0
    int_height: float = 0.0

    # Plywood thickness (mm)
    panel_thickness: float = 9.0

    # Hardware items  [{name, count, part_number, manufacturer}, ...]
    hardware_items: List[Dict] = field(default_factory=list)

    # Panel cut list [{name, width, height, thickness, qty}, ...]
    panels: List[Dict] = field(default_factory=list)

    # Aluminum profile cuts [{profile_type, length, qty}, ...]
    profile_cuts: List[Dict] = field(default_factory=list)

    # Foam items [{type, width, depth, height, qty}, ...]
    foam_items: List[Dict] = field(default_factory=list)

    # Total estimated weight (kg)
    total_weight: float = 0.0

    # Total estimated cost (currency-agnostic units)
    total_cost: float = 0.0

    # Collision warnings
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# CaseManager
# ---------------------------------------------------------------------------

class CaseManager:
    """
    Static-method façade that orchestrates case creation and updates.

    Usage
    -----
    CaseManager.generate(context)   # Create a new case from scratch
    CaseManager.update(obj, context)  # Rebuild dirty sub-systems
    CaseManager.delete(obj, context)  # Remove all case geometry
    """

    # Root-object custom property key that marks it as a flight case root
    ROOT_KEY = "flight_case_root"

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    @classmethod
    def generate(cls, context: bpy.types.Context) -> bpy.types.Object:
        """Create a new flight case in the current scene."""
        from ..templates import get_template
        from ..utils.object_utils import ensure_case_collection

        params: CaseSettings = cls._fresh_params(context)
        project_name = params.project_name or "FlightCase"

        root_collection = ensure_case_collection(project_name, context)

        # Create an empty root object to hold all parameters
        root = cls._create_root_object(project_name, root_collection, context)
        root[cls.ROOT_KEY] = True

        # Copy default params onto root object
        # (PropertyGroup is already attached via bpy.types.Object.flight_case)
        root.flight_case.project_name = project_name

        # Mark all sub-systems dirty for a full build
        root.flight_case.panels_dirty = True
        root.flight_case.hardware_dirty = True
        root.flight_case.foam_dirty = True

        cls._rebuild(root, context)
        return root

    @classmethod
    def update(cls, root_obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Rebuild only dirty sub-systems of an existing case."""
        if not root_obj or cls.ROOT_KEY not in root_obj:
            return
        cls._rebuild(root_obj, context)

    @classmethod
    def delete(cls, root_obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Remove all geometry belonging to this case."""
        if root_obj is None:
            return
        collection_name = root_obj.get("flight_case_collection", "")
        if collection_name and collection_name in bpy.data.collections:
            col = bpy.data.collections[collection_name]
            cls._purge_collection(col)
            bpy.data.collections.remove(col)
        # Remove root object itself
        bpy.data.objects.remove(root_obj, do_unlink=True)

    @classmethod
    def build_case_data(cls, root_obj: bpy.types.Object) -> CaseData:
        """Return a CaseData snapshot for the given root object."""
        from ..manufacturing.bom import build_bom
        from ..manufacturing.cut_list import build_cut_list
        from ..manufacturing.weight import estimate_weight
        from ..core.collision import CollisionChecker

        params: CaseSettings = root_obj.flight_case
        t = float(params.material.thickness_mm)
        eq = params.equipment

        int_w = eq.width  + eq.internal_clearance * 2
        int_d = (eq.depth + eq.cable_clearance
                 + eq.connector_clearance + eq.internal_clearance * 2)
        int_h = eq.height + eq.internal_clearance * 2

        ext_w = int_w + t * 2
        ext_d = int_d + t * 2
        ext_h = int_h + t * 2

        data = CaseData(
            project_name=params.project_name,
            case_type=params.case_type,
            ext_width=ext_w,
            ext_depth=ext_d,
            ext_height=ext_h,
            int_width=int_w,
            int_depth=int_d,
            int_height=int_h,
            panel_thickness=t,
        )

        build_bom(data, root_obj)
        build_cut_list(data, root_obj)
        data.total_weight = estimate_weight(data, root_obj)

        checker = CollisionChecker()
        data.warnings = checker.check(root_obj)

        return data

    # ---------------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------------

    @classmethod
    def _rebuild(cls, root_obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Run the active template's build, honouring dirty flags."""
        from ..templates import get_template
        from ..core.collision import CollisionChecker

        params: CaseSettings = root_obj.flight_case
        template_cls = get_template(params.case_type)
        template = template_cls()

        template.build_geometry(root_obj, params, context)

        # Clear dirty flags after successful build
        params.panels_dirty = False
        params.hardware_dirty = False
        params.foam_dirty = False

        # Run collision checks and annotate warnings
        checker = CollisionChecker()
        warnings = checker.check(root_obj)
        root_obj["flight_case_warnings"] = warnings

    @classmethod
    def _fresh_params(cls, context: bpy.types.Context) -> "CaseSettings":
        """Return the CaseSettings of the active object, or a default stub."""
        obj = context.object
        if obj is not None and hasattr(obj, "flight_case"):
            return obj.flight_case
        # Return a temporary PropertyGroup-like namespace via a dummy object
        # (this path is only hit when there is no active object yet)
        return None

    @classmethod
    def _create_root_object(
        cls,
        name: str,
        collection: bpy.types.Collection,
        context: bpy.types.Context,
    ) -> bpy.types.Object:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "PLAIN_AXES"
        collection.objects.link(empty)
        # Link to scene collection so it is visible
        if empty.name not in context.scene.collection.objects:
            context.scene.collection.objects.link(empty)
        root_col_name = collection.name
        empty["flight_case_collection"] = root_col_name
        return empty

    @classmethod
    def _purge_collection(cls, col: bpy.types.Collection) -> None:
        """Recursively remove all objects and sub-collections."""
        for child in list(col.children):
            cls._purge_collection(child)
            bpy.data.collections.remove(child)
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
