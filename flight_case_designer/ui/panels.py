# SPDX-License-Identifier: GPL-3.0-or-later
"""
Sidebar UI panels for the Flight Case Designer.

All panels appear in the 3-D Viewport sidebar under the «Flight Case» tab.
The tab is organised into collapsible sections that mirror the workflow:

  Project → Equipment → Case → Profiles → Hardware → Foam → Panels → Manufacturing → Export

Each section uses a ``bl_parent_id`` parent so it appears as a sub-panel of
the main «Flight Case» header.
"""

from __future__ import annotations

import bpy
from bpy.types import Panel

_SPACE   = "VIEW_3D"
_REGION  = "UI"
_CATEGORY = "Flight Case"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _header_row(layout, label: str, icon: str = "NONE") -> None:
    """Draw a bold header row."""
    row = layout.row()
    row.label(text=label, icon=icon)


def _prop_col(layout, data, props, **kwargs) -> None:
    """Draw a column of properties."""
    col = layout.column(align=True)
    for attr in props:
        col.prop(data, attr, **kwargs)
    return col


# ---------------------------------------------------------------------------
# Main header panel
# ---------------------------------------------------------------------------

class FCD_PT_main(Panel):
    """Flight Case Designer – main sidebar tab."""

    bl_label       = "Flight Case Designer"
    bl_idname      = "FCD_PT_main"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        props  = context.scene.fcd
        case   = props.case

        # Case name
        layout.prop(case, "case_name", text="", icon="OUTLINER_OB_EMPTY")

        # Primary action buttons
        col = layout.column(align=True)
        col.scale_y = 1.4
        col.operator("fcd.create_case", text="Generate Case", icon="PLAY")
        row = col.row(align=True)
        row.operator("fcd.rebuild_case", text="Rebuild",  icon="FILE_REFRESH")
        row.operator("fcd.clear_case",   text="Clear",    icon="TRASH")

        layout.separator()

        # Quick weight summary
        try:
            from ..generators.case_builder import CaseDimensions
            dims = CaseDimensions(props)
            box = layout.box()
            col = box.column(align=True)
            col.label(text=f"External: {dims.ext_w*1000:.0f} × {dims.ext_d*1000:.0f} × {dims.ext_h*1000:.0f} mm", icon="CUBE")
            col.label(text=f"Est. Total Weight: {dims.total_weight():.1f} kg",  icon="EMPTY_AXIS")
        except (AttributeError, ValueError, ZeroDivisionError):
            # Properties may not be fully initialised on first draw; skip silently.
            pass


# ---------------------------------------------------------------------------
# Project / presets panel
# ---------------------------------------------------------------------------

class FCD_PT_project(Panel):
    bl_label       = "Project & Presets"
    bl_idname      = "FCD_PT_project"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        row = layout.row(align=True)
        row.operator("fcd.save_preset", text="Save Preset", icon="FILE_TICK")
        row.operator("fcd.load_preset", text="Load Preset", icon="FILEBROWSER")


# ---------------------------------------------------------------------------
# Equipment panel
# ---------------------------------------------------------------------------

class FCD_PT_equipment(Panel):
    bl_label       = "Equipment"
    bl_idname      = "FCD_PT_equipment"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        eq     = context.scene.fcd.equipment

        # Dimensions
        box = layout.box()
        box.label(text="Dimensions", icon="OBJECT_DATA")
        col = box.column(align=True)
        col.prop(eq, "equipment_width",  text="Width (mm)")
        col.prop(eq, "equipment_depth",  text="Depth (mm)")
        col.prop(eq, "equipment_height", text="Height (mm)")
        col.prop(eq, "equipment_weight", text="Weight (kg)")
        col.prop(eq, "orientation")

        # Clearances
        box = layout.box()
        box.label(text="Clearances", icon="MOD_EDGESPLIT")
        col = box.column(align=True)
        col.prop(eq, "internal_clearance")
        col.prop(eq, "air_gap")
        col.prop(eq, "cable_clearance")
        col.prop(eq, "connector_clearance")

        # Foam per face
        box = layout.box()
        row = box.row()
        row.label(text="Foam Thickness", icon="MATFLUID")
        row.prop(eq, "asymmetric_foam", text="Asymmetric")

        col = box.column(align=True)
        col.prop(eq, "foam_top",    text="Top")
        col.prop(eq, "foam_bottom", text="Bottom")
        if eq.asymmetric_foam:
            col.prop(eq, "foam_left",  text="Left")
            col.prop(eq, "foam_right", text="Right")
            col.prop(eq, "foam_front", text="Front")
            col.prop(eq, "foam_back",  text="Back")
        else:
            col.prop(eq, "foam_left",  text="Sides / Front / Back")

        col.prop(eq, "foam_compression", text="Compression (%)")


# ---------------------------------------------------------------------------
# Case construction panel
# ---------------------------------------------------------------------------

class FCD_PT_case(Panel):
    bl_label       = "Case Construction"
    bl_idname      = "FCD_PT_case"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        case   = context.scene.fcd.case

        col = layout.column(align=True)
        col.prop(case, "case_type")

        # Rack-case extra settings
        if case.case_type == "RACK_CASE":
            box = layout.box()
            box.label(text="Rack Settings", icon="MESH_GRID")
            col2 = box.column(align=True)
            col2.prop(case, "rack_units")
            col2.prop(case, "rack_depth")
        elif case.case_type not in ("CUSTOM_BOX",):
            col.prop(case, "lid_height_ratio")

        # Plywood
        box = layout.box()
        box.label(text="Plywood", icon="TEXTURE")
        bcol = box.column(align=True)
        bcol.prop(case, "ply_thickness_preset", text="Thickness")
        if case.ply_thickness_preset == "CUSTOM":
            bcol.prop(case, "ply_thickness_custom")
        bcol.prop(case, "material_type")
        bcol.prop(case, "generate_rebates")

        # Visibility toggles
        box = layout.box()
        box.label(text="Show / Hide", icon="HIDE_OFF")
        row = box.row(align=True)
        row.prop(case, "show_foam",      text="Foam",      toggle=True)
        row.prop(case, "show_hardware",  text="HW",        toggle=True)
        row.prop(case, "show_profiles",  text="Profiles",  toggle=True)
        row2 = box.row(align=True)
        row2.prop(case, "show_rivets",   text="Rivets",    toggle=True)
        row2.prop(case, "show_equipment",text="Equipment", toggle=True)


# ---------------------------------------------------------------------------
# Profiles panel
# ---------------------------------------------------------------------------

class FCD_PT_profiles(Panel):
    bl_label       = "Aluminium Profiles"
    bl_idname      = "FCD_PT_profiles"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        case   = context.scene.fcd.case

        col = layout.column(align=True)
        col.prop(case, "profile_type")
        col.prop(case, "profile_size")
        col.prop(case, "corner_type")

        # Profile catalog reference
        from ..libraries.profile_data import PROFILE_CATALOG
        box = layout.box()
        box.label(text=f"Catalog: {len(PROFILE_CATALOG)} profiles available", icon="INFO")


# ---------------------------------------------------------------------------
# Hardware panel
# ---------------------------------------------------------------------------

class FCD_PT_hardware(Panel):
    bl_label       = "Hardware"
    bl_idname      = "FCD_PT_hardware"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        hdw    = context.scene.fcd.hardware
        case   = context.scene.fcd.case

        # Latches
        box = layout.box()
        box.label(text="Latches", icon="SNAP_FACE")
        col = box.column(align=True)
        col.prop(hdw, "latch_type")
        if hdw.latch_type != "NONE":
            col.prop(hdw, "latch_count")

        # Handles
        box = layout.box()
        box.label(text="Handles", icon="ORIENTATION_GIMBAL")
        col = box.column(align=True)
        col.prop(hdw, "handle_type")
        if hdw.handle_type != "NONE":
            col.prop(hdw, "handle_count")

        # Feet
        box = layout.box()
        box.label(text="Feet / Casters", icon="CON_PIVOT")
        box.prop(hdw, "feet_type")

        # Hinges
        if case.case_type == "HINGED_LID":
            box = layout.box()
            box.label(text="Hinges", icon="DECORATE_LINKED")
            box.prop(hdw, "hinge_count")

        # Extras
        box = layout.box()
        box.label(text="Extras", icon="PLUS")
        row = box.row(align=True)
        row.prop(hdw, "stacking_cups", toggle=True)
        row.prop(hdw, "label_holder",  toggle=True)

        # Rivets
        box = layout.box()
        box.label(text="Rivets", icon="PARTICLE_POINT")
        col = box.column(align=True)
        col.prop(hdw, "show_rivets")
        if hdw.show_rivets:
            col.prop(hdw, "rivet_spacing")
            col.prop(hdw, "rivet_edge_offset")
            col.prop(hdw, "rivet_diameter")

        # Hardware catalog reference
        from ..libraries.hardware_data import HARDWARE_CATALOG
        layout.label(
            text=f"Catalog: {len(HARDWARE_CATALOG)} items",
            icon="INFO",
        )


# ---------------------------------------------------------------------------
# Foam panel
# ---------------------------------------------------------------------------

class FCD_PT_foam(Panel):
    bl_label       = "Foam"
    bl_idname      = "FCD_PT_foam"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        foam   = context.scene.fcd.foam

        col = layout.column(align=True)
        col.prop(foam, "foam_type")
        col.prop(foam, "foam_density")
        col.prop(foam, "cutout_style")

        if foam.cutout_style == "FINGER_PULL":
            box = layout.box()
            box.label(text="Finger Pull Settings")
            col2 = box.column(align=True)
            col2.prop(foam, "finger_pull_depth")
            col2.prop(foam, "finger_pull_width")


# ---------------------------------------------------------------------------
# Manufacturing panel
# ---------------------------------------------------------------------------

class FCD_PT_manufacturing(Panel):
    bl_label       = "Manufacturing"
    bl_idname      = "FCD_PT_manufacturing"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        mfg    = context.scene.fcd.manufacturing

        try:
            from ..generators.case_builder import CaseDimensions
            from ..exporters.bom_exporter  import _collect_panels, _collect_profiles, _panel_area_sqm, _profile_total_m

            props = context.scene.fcd
            dims  = CaseDimensions(props)
            panels   = _collect_panels(dims)
            profiles = _collect_profiles(dims)

            box = layout.box()
            box.label(text="Quick Summary", icon="PROPERTIES")
            col = box.column(align=True)
            col.label(text=f"Panels: {len(panels)} pieces ({_panel_area_sqm(panels):.3f} m²)")
            col.label(text=f"Profiles: {len(profiles)} cuts ({_profile_total_m(profiles):.2f} m)")
            col.label(text=f"Plywood: {dims.ply_weight:.2f} kg")
            col.label(text=f"Total weight: {dims.total_weight():.2f} kg")
        except (AttributeError, ValueError, ZeroDivisionError):
            # Properties may not be fully initialised on first draw; skip silently.
            pass

        # Cost estimate toggle
        box = layout.box()
        box.label(text="Cost Estimate", icon="FUND")
        col = box.column(align=True)
        col.prop(mfg, "include_cost_estimate")
        if mfg.include_cost_estimate:
            col.prop(mfg, "ply_cost_per_sqm")
            col.prop(mfg, "foam_cost_per_sqm")
            col.prop(mfg, "profile_cost_per_m")
            col.prop(mfg, "hardware_markup")


# ---------------------------------------------------------------------------
# Export panel
# ---------------------------------------------------------------------------

class FCD_PT_export(Panel):
    bl_label       = "Export"
    bl_idname      = "FCD_PT_export"
    bl_space_type  = _SPACE
    bl_region_type = _REGION
    bl_category    = _CATEGORY
    bl_parent_id   = "FCD_PT_main"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        mfg    = context.scene.fcd.manufacturing

        col = layout.column(align=True)
        col.label(text="Export Directory", icon="FILE_FOLDER")
        col.prop(mfg, "export_path", text="")

        layout.separator()
        col2 = layout.column(align=True)
        col2.scale_y = 1.2
        col2.operator("fcd.export_bom", text="Export Cut List & BOM", icon="EXPORT")

        layout.separator()
        row = layout.row(align=True)
        row.operator("fcd.save_preset", text="Save Preset", icon="FILE_TICK")
        row.operator("fcd.load_preset", text="Load Preset", icon="FILEBROWSER")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_CLASSES = [
    FCD_PT_main,
    FCD_PT_project,
    FCD_PT_equipment,
    FCD_PT_case,
    FCD_PT_profiles,
    FCD_PT_hardware,
    FCD_PT_foam,
    FCD_PT_manufacturing,
    FCD_PT_export,
]


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
