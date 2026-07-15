# SPDX-License-Identifier: GPL-3.0-or-later
"""
All PropertyGroup classes for the Flight Case Designer.

Each group maps to one section of the UI sidebar.  Properties are stored on
``bpy.context.scene.fcd`` so that multiple cases can share settings during a
session while still being independently editable by saving/loading presets.

An ``update_case`` callback is attached to every user-facing property so that
any change immediately triggers a full rebuild.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

# ---------------------------------------------------------------------------
# Enumeration items (shared between properties and UI)
# ---------------------------------------------------------------------------

CASE_TYPE_ITEMS = [
    ("LIFTOFF_LID",    "Lift-off Lid",    "Standard case with removable lid"),
    ("HINGED_LID",     "Hinged Lid",      "Case with hinged lid"),
    ("RACK_CASE",      "Rack Case (19\")", "19\" rack-mount case"),
    ("TRUNK",          "Trunk",           "Large trunk-style case"),
    ("CABLE_DOGHOUSE", "Cable Doghouse",  "Cable management case"),
    ("DRAWER_CASE",    "Drawer Case",     "Case with internal drawers"),
    ("SPEAKER_CASE",   "Speaker Case",    "Speaker enclosure case"),
    ("AMPLIFIER_CASE", "Amplifier Case",  "Amplifier / power-amp case"),
    ("MIXER_CASE",     "Mixer Case",      "Mixing-console case"),
    ("KEYBOARD_CASE",  "Keyboard Case",   "Keyboard / synthesiser case"),
    ("CUSTOM_BOX",     "Custom Box",      "Fully custom dimensions"),
]

PLY_THICKNESS_ITEMS = [
    ("6",      "6 mm",   "6 mm plywood"),
    ("7",      "7 mm",   "7 mm plywood"),
    ("9",      "9 mm",   "9 mm plywood"),
    ("12",     "12 mm",  "12 mm plywood"),
    ("CUSTOM", "Custom", "Custom thickness"),
]

MATERIAL_TYPE_ITEMS = [
    ("BIRCH",         "Birch",         "Standard birch plywood"),
    ("PHENOLIC_BIRCH","Phenolic Birch", "Phenolic-coated birch"),
    ("MDF",           "MDF",           "Medium-density fibreboard"),
]

FOAM_TYPE_ITEMS = [
    ("EVA", "EVA", "Ethylene-vinyl acetate foam"),
    ("PE",  "PE",  "Polyethylene foam"),
    ("PU",  "PU",  "Polyurethane foam"),
]

ORIENTATION_ITEMS = [
    ("FLAT",     "Flat",     "Equipment mounted flat"),
    ("UPRIGHT",  "Upright",  "Equipment standing upright"),
    ("INVERTED", "Inverted", "Equipment inverted"),
]

PROFILE_TYPE_ITEMS = [
    ("ANGLE",        "Angle",          "L-shaped angle extrusion"),
    ("DOUBLE_ANGLE", "Double Angle",   "Double-angle extrusion"),
    ("TONGUE_GROOVE","Tongue & Groove","Tongue-and-groove profile"),
    ("LID_PROFILE",  "Lid Profile",    "Lid closure profile"),
    ("H_PROFILE",    "H Profile",      "H-section extrusion"),
    ("CORNER_PROFILE","Corner Profile","Corner-bracket extrusion"),
]

CORNER_TYPE_ITEMS = [
    ("BALL", "Ball Corners",  "Rounded 9-hole ball corners"),
    ("CAST", "Cast Corners",  "Heavy-duty cast recessed corners"),
    ("NONE", "No Corners",    "No corner hardware"),
]

LATCH_TYPE_ITEMS = [
    ("BUTTERFLY", "Butterfly Latch", "Standard butterfly latch"),
    ("DRAW",      "Draw Latch",      "Draw-bolt latch"),
    ("NONE",      "No Latches",      "No latches"),
]

HANDLE_TYPE_ITEMS = [
    ("SPRING", "Spring Handle", "Spring-loaded recessed handle"),
    ("SIDE",   "Side Handle",   "Fixed side grip handle"),
    ("NONE",   "No Handles",    "No handles"),
]

FEET_TYPE_ITEMS = [
    ("RUBBER",  "Rubber Feet", "Anti-slip rubber feet"),
    ("CASTERS", "Casters",     "Swivel casters with brakes"),
    ("NONE",    "None",        "No feet"),
]

FOAM_CUTOUT_ITEMS = [
    ("NONE",        "No Cutout",    "Solid foam block"),
    ("SIMPLE",      "Simple Block", "Rectangular cutout"),
    ("OFFSET",      "Offset",       "Offset inset cutout"),
    ("FINGER_PULL", "Finger Pull",  "Finger-pull grooves"),
    ("MULTI_LAYER", "Multi Layer",  "Multiple stacked layers"),
]


# ---------------------------------------------------------------------------
# Update callback
# ---------------------------------------------------------------------------

def _update_case(self, context: bpy.types.Context) -> None:
    """Rebuild active case whenever any tracked property changes."""
    # Deferred so the property system finishes its own bookkeeping first.
    bpy.app.timers.register(_rebuild_timer, first_interval=0.0)


def _rebuild_timer() -> None:
    """Timer target – runs the rebuild operator once then stops."""
    ctx = bpy.context
    if ctx.area is not None:
        try:
            bpy.ops.fcd.rebuild_case()
        except Exception:  # noqa: BLE001
            pass
    return None  # returning None cancels the timer


# ---------------------------------------------------------------------------
# Property groups
# ---------------------------------------------------------------------------

class FCD_EquipmentProperties(PropertyGroup):
    """Equipment dimensions, orientation, clearances and per-face foam."""

    equipment_width: FloatProperty(
        name="Width (mm)",
        description="Equipment width in millimetres",
        default=500.0, min=1.0, max=5000.0,
        update=_update_case,
    )
    equipment_depth: FloatProperty(
        name="Depth (mm)",
        description="Equipment depth (front-to-back) in millimetres",
        default=400.0, min=1.0, max=5000.0,
        update=_update_case,
    )
    equipment_height: FloatProperty(
        name="Height (mm)",
        description="Equipment height in millimetres",
        default=200.0, min=1.0, max=5000.0,
        update=_update_case,
    )
    equipment_weight: FloatProperty(
        name="Weight (kg)",
        description="Equipment weight in kilograms (drives hardware rules)",
        default=10.0, min=0.0, max=1000.0,
        update=_update_case,
    )
    orientation: EnumProperty(
        name="Orientation",
        description="Equipment mounting orientation inside the case",
        items=ORIENTATION_ITEMS,
        default="FLAT",
        update=_update_case,
    )

    # Clearances
    cable_clearance: FloatProperty(
        name="Cable Clearance (mm)",
        description="Extra room for cable exits",
        default=30.0, min=0.0, max=200.0,
        update=_update_case,
    )
    connector_clearance: FloatProperty(
        name="Connector Clearance (mm)",
        description="Extra room for connectors",
        default=20.0, min=0.0, max=200.0,
        update=_update_case,
    )
    internal_clearance: FloatProperty(
        name="Internal Clearance (mm)",
        description="General gap between equipment and foam",
        default=5.0, min=0.0, max=100.0,
        update=_update_case,
    )
    air_gap: FloatProperty(
        name="Air Gap (mm)",
        description="Ventilation gap around equipment",
        default=3.0, min=0.0, max=50.0,
        update=_update_case,
    )

    # Per-face foam thickness
    asymmetric_foam: BoolProperty(
        name="Asymmetric Foam",
        description="Set different foam thicknesses per side",
        default=False,
        update=_update_case,
    )
    foam_top: FloatProperty(
        name="Foam Top (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_bottom: FloatProperty(
        name="Foam Bottom (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_left: FloatProperty(
        name="Foam Left (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_right: FloatProperty(
        name="Foam Right (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_front: FloatProperty(
        name="Foam Front (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_back: FloatProperty(
        name="Foam Back (mm)", default=25.0, min=0.0, max=200.0,
        update=_update_case,
    )
    foam_compression: FloatProperty(
        name="Foam Compression (%)",
        description="Percentage by which foam is compressed when lid is closed",
        default=10.0, min=0.0, max=50.0,
        update=_update_case,
    )

    @property
    def uniform_foam(self) -> float:
        """Return average foam thickness for quick calculations."""
        return (
            self.foam_top + self.foam_bottom
            + self.foam_left + self.foam_right
            + self.foam_front + self.foam_back
        ) / 6.0


class FCD_CaseProperties(PropertyGroup):
    """Case construction type, material and component visibility."""

    case_name: StringProperty(
        name="Case Name",
        description="Project name shown in the collection hierarchy",
        default="Flight Case",
    )
    case_type: EnumProperty(
        name="Case Type",
        items=CASE_TYPE_ITEMS,
        default="LIFTOFF_LID",
        update=_update_case,
    )

    # Plywood
    ply_thickness_preset: EnumProperty(
        name="Plywood Thickness",
        items=PLY_THICKNESS_ITEMS,
        default="9",
        update=_update_case,
    )
    ply_thickness_custom: FloatProperty(
        name="Custom Thickness (mm)",
        default=9.0, min=1.0, max=50.0,
        update=_update_case,
    )
    material_type: EnumProperty(
        name="Material Type",
        items=MATERIAL_TYPE_ITEMS,
        default="BIRCH",
        update=_update_case,
    )

    # Lid split
    lid_height_ratio: FloatProperty(
        name="Lid Height Ratio",
        description="Lid height as a fraction of total external case height",
        default=0.35, min=0.05, max=0.90,
        update=_update_case,
    )

    # Rack case extras
    rack_units: IntProperty(
        name="Rack Units (U)",
        description="Number of 1U (44.45 mm) rack slots",
        default=4, min=1, max=100,
        update=_update_case,
    )
    rack_depth: FloatProperty(
        name="Rack Depth (mm)",
        description="Internal depth available for rack-mounted equipment",
        default=400.0, min=100.0, max=1000.0,
        update=_update_case,
    )

    # Profiles
    profile_type: EnumProperty(
        name="Profile Type",
        items=PROFILE_TYPE_ITEMS,
        default="ANGLE",
        update=_update_case,
    )
    profile_size: FloatProperty(
        name="Profile Size (mm)",
        description="Nominal profile leg / flange dimension",
        default=30.0, min=10.0, max=80.0,
        update=_update_case,
    )

    # Corners
    corner_type: EnumProperty(
        name="Corner Type",
        items=CORNER_TYPE_ITEMS,
        default="BALL",
        update=_update_case,
    )

    # Rebates
    generate_rebates: BoolProperty(
        name="Generate Rebates",
        description="Cut rebate grooves into panel edges for profile seating",
        default=False,
        update=_update_case,
    )

    # Component visibility toggles
    show_foam: BoolProperty(name="Foam", default=True, update=_update_case)
    show_hardware: BoolProperty(name="Hardware", default=True, update=_update_case)
    show_profiles: BoolProperty(name="Profiles", default=True, update=_update_case)
    show_rivets: BoolProperty(name="Rivets", default=False, update=_update_case)
    show_equipment: BoolProperty(name="Equipment Ghost", default=True, update=_update_case)


class FCD_FoamProperties(PropertyGroup):
    """Foam material type and cutout style."""

    foam_type: EnumProperty(
        name="Foam Type",
        items=FOAM_TYPE_ITEMS,
        default="PE",
        update=_update_case,
    )
    foam_density: FloatProperty(
        name="Density (kg/m³)",
        default=30.0, min=5.0, max=200.0,
        update=_update_case,
    )
    cutout_style: EnumProperty(
        name="Cutout Style",
        items=FOAM_CUTOUT_ITEMS,
        default="SIMPLE",
        update=_update_case,
    )
    finger_pull_depth: FloatProperty(
        name="Finger Pull Depth (mm)", default=15.0, min=5.0, max=50.0,
        update=_update_case,
    )
    finger_pull_width: FloatProperty(
        name="Finger Pull Width (mm)", default=25.0, min=10.0, max=80.0,
        update=_update_case,
    )
    cable_channel_width: FloatProperty(
        name="Cable Channel Width (mm)", default=30.0, min=10.0, max=100.0,
        update=_update_case,
    )


class FCD_HardwareProperties(PropertyGroup):
    """Hardware selection and automatic-placement settings."""

    # Latches
    latch_type: EnumProperty(
        name="Latch Type",
        items=LATCH_TYPE_ITEMS,
        default="BUTTERFLY",
        update=_update_case,
    )
    latch_count: IntProperty(
        name="Latch Count (0 = auto)",
        default=0, min=0, max=20,
        update=_update_case,
    )

    # Handles
    handle_type: EnumProperty(
        name="Handle Type",
        items=HANDLE_TYPE_ITEMS,
        default="SPRING",
        update=_update_case,
    )
    handle_count: IntProperty(
        name="Handles per Side (0 = auto)",
        default=0, min=0, max=6,
        update=_update_case,
    )

    # Feet / casters
    feet_type: EnumProperty(
        name="Feet / Casters",
        items=FEET_TYPE_ITEMS,
        default="RUBBER",
        update=_update_case,
    )

    # Optional extras
    stacking_cups: BoolProperty(
        name="Stacking Cups",
        description="Add stacking-cup inserts for safe case stacking",
        default=False,
        update=_update_case,
    )
    label_holder: BoolProperty(
        name="Label Holder",
        description="Add a label / tag holder to the case front",
        default=True,
        update=_update_case,
    )
    hinge_count: IntProperty(
        name="Hinge Count",
        description="Number of lid hinges (hinged-lid cases only)",
        default=2, min=1, max=8,
        update=_update_case,
    )

    # Rivets
    show_rivets: BoolProperty(
        name="Generate Rivets",
        description="Show blind-rivet geometry on all hardware",
        default=False,
        update=_update_case,
    )
    rivet_spacing: FloatProperty(
        name="Rivet Spacing (mm)",
        default=80.0, min=20.0, max=300.0,
        update=_update_case,
    )
    rivet_edge_offset: FloatProperty(
        name="Edge Offset (mm)",
        description="Distance from panel edge to first/last rivet",
        default=8.0, min=2.0, max=30.0,
        update=_update_case,
    )
    rivet_diameter: FloatProperty(
        name="Rivet Diameter (mm)",
        default=4.8, min=2.0, max=10.0,
        update=_update_case,
    )


class FCD_ManufacturingProperties(PropertyGroup):
    """Export paths and optional cost-estimation settings."""

    export_path: StringProperty(
        name="Export Path",
        description="Directory where cut-list / BOM files are written",
        default="//",
        subtype="DIR_PATH",
    )
    include_cost_estimate: BoolProperty(
        name="Include Cost Estimate",
        default=False,
    )
    ply_cost_per_sqm: FloatProperty(
        name="Plywood Cost (£/m²)", default=15.0, min=0.0,
    )
    foam_cost_per_sqm: FloatProperty(
        name="Foam Cost (£/m²)", default=8.0, min=0.0,
    )
    profile_cost_per_m: FloatProperty(
        name="Profile Cost (£/m)", default=5.0, min=0.0,
    )
    hardware_markup: FloatProperty(
        name="Hardware Markup (%)", default=20.0, min=0.0,
    )


class FCD_SceneProperties(PropertyGroup):
    """Root property group attached to bpy.types.Scene as ``scene.fcd``."""

    equipment:     PointerProperty(type=FCD_EquipmentProperties)
    case:          PointerProperty(type=FCD_CaseProperties)
    foam:          PointerProperty(type=FCD_FoamProperties)
    hardware:      PointerProperty(type=FCD_HardwareProperties)
    manufacturing: PointerProperty(type=FCD_ManufacturingProperties)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_CLASSES = [
    FCD_EquipmentProperties,
    FCD_CaseProperties,
    FCD_FoamProperties,
    FCD_HardwareProperties,
    FCD_ManufacturingProperties,
    FCD_SceneProperties,
]


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fcd = PointerProperty(type=FCD_SceneProperties)


def unregister() -> None:
    del bpy.types.Scene.fcd
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
