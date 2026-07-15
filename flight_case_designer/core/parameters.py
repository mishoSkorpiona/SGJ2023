"""
core/parameters.py — All Blender PropertyGroup definitions for the add-on.

Every property uses an ``update`` callback so that changing any value
automatically triggers a case regeneration via the CaseManager.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup


# ---------------------------------------------------------------------------
# Helper — deferred import to avoid circular references at module load time
# ---------------------------------------------------------------------------

def _trigger_update(self, context: bpy.types.Context) -> None:
    """Generic update callback: request a case rebuild."""
    from .case_manager import CaseManager
    obj = context.object
    if obj is not None and "flight_case_root" in obj:
        CaseManager.update(obj, context)


# ---------------------------------------------------------------------------
# Equipment Settings
# ---------------------------------------------------------------------------

class EquipmentSettings(PropertyGroup):
    """Dimensions and clearances of the equipment to be housed."""

    width: FloatProperty(
        name="Width",
        description="Equipment width (mm)",
        default=482.6,
        min=10.0,
        max=5000.0,
        unit="NONE",
        update=_trigger_update,
    )
    depth: FloatProperty(
        name="Depth",
        description="Equipment depth (mm)",
        default=300.0,
        min=10.0,
        max=5000.0,
        unit="NONE",
        update=_trigger_update,
    )
    height: FloatProperty(
        name="Height",
        description="Equipment height (mm)",
        default=44.45,
        min=1.0,
        max=5000.0,
        unit="NONE",
        update=_trigger_update,
    )
    weight: FloatProperty(
        name="Weight",
        description="Equipment weight (kg)",
        default=5.0,
        min=0.0,
        max=2000.0,
        update=_trigger_update,
    )
    orientation: EnumProperty(
        name="Orientation",
        description="How the equipment sits inside the case",
        items=[
            ("HORIZONTAL", "Horizontal", "Landscape orientation"),
            ("VERTICAL", "Vertical", "Portrait orientation"),
            ("FLAT", "Flat", "Flat / on its back"),
        ],
        default="HORIZONTAL",
        update=_trigger_update,
    )

    # Clearances
    cable_clearance: FloatProperty(
        name="Cable Clearance",
        description="Extra space behind equipment for cable routing (mm)",
        default=50.0,
        min=0.0,
        max=500.0,
        update=_trigger_update,
    )
    connector_clearance: FloatProperty(
        name="Connector Clearance",
        description="Extra space at front for connectors / front-panel depth (mm)",
        default=20.0,
        min=0.0,
        max=500.0,
        update=_trigger_update,
    )
    internal_clearance: FloatProperty(
        name="Internal Clearance",
        description="General air gap around the equipment on all sides (mm)",
        default=5.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    air_gap: FloatProperty(
        name="Air Gap",
        description="Ventilation gap (mm)",
        default=10.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )


# ---------------------------------------------------------------------------
# Foam Settings
# ---------------------------------------------------------------------------

class FoamSettings(PropertyGroup):
    """Foam padding parameters — each face can be set independently."""

    foam_type: EnumProperty(
        name="Foam Type",
        items=[
            ("EVA", "EVA", "Ethylene-vinyl acetate foam"),
            ("PE", "PE", "Polyethylene foam"),
            ("PU", "PU", "Polyurethane foam"),
        ],
        default="PE",
        update=_trigger_update,
    )
    density: FloatProperty(
        name="Density (kg/m³)",
        description="Foam density in kg/m³",
        default=30.0,
        min=5.0,
        max=200.0,
        update=_trigger_update,
    )
    compression: FloatProperty(
        name="Compression",
        description="Foam compression ratio (0–1)",
        default=0.1,
        min=0.0,
        max=0.5,
        update=_trigger_update,
    )

    # Per-side thickness
    top: FloatProperty(
        name="Top",
        description="Top foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    bottom: FloatProperty(
        name="Bottom",
        description="Bottom foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    front: FloatProperty(
        name="Front",
        description="Front foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    back: FloatProperty(
        name="Back",
        description="Back foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    left: FloatProperty(
        name="Left",
        description="Left foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )
    right: FloatProperty(
        name="Right",
        description="Right foam thickness (mm)",
        default=25.0,
        min=0.0,
        max=200.0,
        update=_trigger_update,
    )

    asymmetric: BoolProperty(
        name="Asymmetric Foam",
        description="Allow different thickness per side",
        default=False,
        update=_trigger_update,
    )
    finger_pulls: BoolProperty(
        name="Finger Pull Cutouts",
        description="Add finger pull notches to foam",
        default=True,
        update=_trigger_update,
    )
    cable_channels: BoolProperty(
        name="Cable Channels",
        description="Route cable channels through foam",
        default=False,
        update=_trigger_update,
    )
    multi_layer: BoolProperty(
        name="Multi-layer Foam",
        description="Use multiple foam layers",
        default=False,
        update=_trigger_update,
    )


# ---------------------------------------------------------------------------
# Material Settings
# ---------------------------------------------------------------------------

class MaterialSettings(PropertyGroup):
    """Construction material selection."""

    plywood_thickness: EnumProperty(
        name="Plywood Thickness",
        items=[
            ("6",  "6 mm",     "6 mm plywood"),
            ("7",  "7 mm",     "7 mm plywood"),
            ("9",  "9 mm",     "9 mm plywood"),
            ("12", "12 mm",    "12 mm plywood"),
            ("0",  "Custom",   "Custom thickness"),
        ],
        default="9",
        update=_trigger_update,
    )
    plywood_thickness_custom: FloatProperty(
        name="Custom Thickness (mm)",
        default=9.0,
        min=1.0,
        max=50.0,
        update=_trigger_update,
    )
    plywood_type: EnumProperty(
        name="Plywood Type",
        items=[
            ("BIRCH",    "Birch",          "Standard birch plywood"),
            ("PHENOLIC", "Phenolic Birch", "Phenolic-faced birch plywood"),
            ("MDF",      "MDF",            "Medium-density fibreboard"),
        ],
        default="BIRCH",
        update=_trigger_update,
    )

    @property
    def thickness_mm(self) -> float:
        """Return effective plywood thickness in mm."""
        if self.plywood_thickness == "0":
            return self.plywood_thickness_custom
        return float(self.plywood_thickness)


# ---------------------------------------------------------------------------
# Profile Settings
# ---------------------------------------------------------------------------

class ProfileSettings(PropertyGroup):
    """Aluminium extrusion profile selection per edge group."""

    profile_type: EnumProperty(
        name="Profile Type",
        items=[
            ("ANGLE",        "Angle",          "Simple L-angle"),
            ("DOUBLE_ANGLE", "Double Angle",   "Double L-angle"),
            ("TONGUE_GROOVE","Tongue & Groove","Tongue and groove"),
            ("LID",          "Lid Profile",    "Lid extrusion"),
            ("H_PROFILE",    "H Profile",      "H-section profile"),
            ("CORNER",       "Corner Profile", "Corner extrusion"),
        ],
        default="ANGLE",
        update=_trigger_update,
    )
    custom_profile_name: StringProperty(
        name="Custom Profile",
        description="Name of user-defined profile from the library",
        default="",
        update=_trigger_update,
    )


# ---------------------------------------------------------------------------
# Hardware Settings
# ---------------------------------------------------------------------------

class HardwareSettings(PropertyGroup):
    """Hardware placement parameters."""

    auto_placement: BoolProperty(
        name="Auto Placement",
        description="Automatically place hardware based on case size and weight",
        default=True,
        update=_trigger_update,
    )
    butterfly_latches: BoolProperty(
        name="Butterfly Latches",
        default=True,
        update=_trigger_update,
    )
    spring_handles: BoolProperty(
        name="Spring Handles",
        default=True,
        update=_trigger_update,
    )
    ball_corners: BoolProperty(
        name="Ball Corners",
        default=True,
        update=_trigger_update,
    )
    cast_corners: BoolProperty(
        name="Cast Corners",
        default=False,
        update=_trigger_update,
    )
    hinges: BoolProperty(
        name="Hinges",
        default=False,
        update=_trigger_update,
    )
    rubber_feet: BoolProperty(
        name="Rubber Feet",
        default=True,
        update=_trigger_update,
    )
    casters: BoolProperty(
        name="Casters / Wheels",
        default=False,
        update=_trigger_update,
    )
    rack_rails: BoolProperty(
        name="Rack Rails",
        default=False,
        update=_trigger_update,
    )
    stacking_cups: BoolProperty(
        name="Stacking Cups",
        default=False,
        update=_trigger_update,
    )
    label_holders: BoolProperty(
        name="Label Holders",
        default=False,
        update=_trigger_update,
    )


# ---------------------------------------------------------------------------
# Rivet Settings
# ---------------------------------------------------------------------------

class RivetSettings(PropertyGroup):
    """Parameters for automatic rivet generation."""

    spacing: FloatProperty(
        name="Spacing (mm)",
        description="Distance between rivets",
        default=50.0,
        min=10.0,
        max=500.0,
        update=_trigger_update,
    )
    edge_offset: FloatProperty(
        name="Edge Offset (mm)",
        description="Offset from edge to first/last rivet",
        default=15.0,
        min=5.0,
        max=100.0,
        update=_trigger_update,
    )
    diameter: FloatProperty(
        name="Diameter (mm)",
        description="Rivet diameter",
        default=4.0,
        min=2.0,
        max=10.0,
        update=_trigger_update,
    )
    corner_skip: BoolProperty(
        name="Skip Corners",
        description="Leave corner zones rivet-free",
        default=True,
        update=_trigger_update,
    )


# ---------------------------------------------------------------------------
# Project / Case Root Settings
# ---------------------------------------------------------------------------

class CaseSettings(PropertyGroup):
    """Top-level case type and project metadata."""

    project_name: StringProperty(
        name="Project Name",
        default="My Flight Case",
        update=_trigger_update,
    )
    case_type: EnumProperty(
        name="Case Type",
        items=[
            ("LIFT_OFF_LID",   "Lift-off Lid",    "Detachable lid case"),
            ("HINGED_LID",     "Hinged Lid",      "Hinged lid case"),
            ("RACK_CASE",      "Rack Case (19\")", "19\" rack mount case"),
            ("TRUNK",          "Trunk",           "Trunk-style case"),
            ("CABLE_DOGHOUSE", "Cable Doghouse",  "Cable storage case"),
            ("DRAWER_CASE",    "Drawer Case",     "Case with drawers"),
            ("SPEAKER_CASE",   "Speaker Case",    "Loudspeaker case"),
            ("AMPLIFIER_CASE", "Amplifier Case",  "Amplifier case"),
            ("MIXER_CASE",     "Mixer Case",      "Mixing console case"),
            ("KEYBOARD_CASE",  "Keyboard Case",   "Keyboard instrument case"),
            ("CUSTOM_BOX",     "Custom Box",      "Fully custom box"),
        ],
        default="LIFT_OFF_LID",
        update=_trigger_update,
    )

    # Rack-specific
    rack_units: IntProperty(
        name="Rack Units (U)",
        description="Number of rack units (1U = 44.45 mm)",
        default=4,
        min=1,
        max=48,
        update=_trigger_update,
    )

    # Dirty flags for partial regeneration
    panels_dirty: BoolProperty(name="Panels Dirty", default=True)
    hardware_dirty: BoolProperty(name="Hardware Dirty", default=True)
    foam_dirty: BoolProperty(name="Foam Dirty", default=True)

    # Sub-property groups
    equipment: PointerProperty(type=EquipmentSettings)
    foam: PointerProperty(type=FoamSettings)
    material: PointerProperty(type=MaterialSettings)
    profile: PointerProperty(type=ProfileSettings)
    hardware: PointerProperty(type=HardwareSettings)
    rivet: PointerProperty(type=RivetSettings)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_CLASSES = [
    EquipmentSettings,
    FoamSettings,
    MaterialSettings,
    ProfileSettings,
    HardwareSettings,
    RivetSettings,
    CaseSettings,
]


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Object.flight_case = PointerProperty(type=CaseSettings)


def unregister() -> None:
    del bpy.types.Object.flight_case
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
