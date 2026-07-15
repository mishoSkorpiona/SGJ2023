"""
ui/operators.py — All Blender operators for the Flight Case Designer.

Operators
---------
FC_OT_CreateFlightCase    — Create a new parametric flight case.
FC_OT_UpdateFlightCase    — Rebuild the active flight case (dirty rebuild).
FC_OT_DeleteFlightCase    — Remove all geometry belonging to the active case.
FC_OT_SavePreset          — Save current settings as a preset file.
FC_OT_LoadPreset          — Load settings from a preset file.
FC_OT_ExportDXF           — Export to DXF.
FC_OT_ExportSVG           — Export to SVG.
FC_OT_ExportPDF           — Export to PDF.
FC_OT_ExportCSV           — Export to CSV.
FC_OT_ExportExcel         — Export to Excel XLSX.
FC_OT_ExportSTL           — Export to STL.
FC_OT_ExportSTEP          — Export to STEP.
FC_OT_GenerateDrawings    — Create drawing cameras.
FC_OT_ExplodedView        — Toggle exploded view.
"""

from __future__ import annotations

import bpy
from bpy.props import StringProperty
from bpy.types import Operator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active_case_root(context: bpy.types.Context):
    obj = context.object
    if obj and "flight_case_root" in obj:
        return obj
    # Search scene for any flight case root
    for obj in context.scene.objects:
        if "flight_case_root" in obj:
            return obj
    return None


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class FC_OT_CreateFlightCase(Operator):
    bl_idname = "flight_case.create"
    bl_label = "Create Flight Case"
    bl_description = "Generate a new parametric flight case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        try:
            root = CaseManager.generate(context)
            context.view_layer.objects.active = root
            self.report({"INFO"}, f"Created flight case '{root.name}'")
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class FC_OT_UpdateFlightCase(Operator):
    bl_idname = "flight_case.update"
    bl_label = "Update Flight Case"
    bl_description = "Rebuild the active flight case with current settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case found.")
            return {"CANCELLED"}
        root.flight_case.panels_dirty = True
        root.flight_case.hardware_dirty = True
        root.flight_case.foam_dirty = True
        CaseManager.update(root, context)

        warnings = root.get("flight_case_warnings", [])
        for w in warnings:
            self.report({"WARNING"}, w)
        self.report({"INFO"}, "Flight case updated.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class FC_OT_DeleteFlightCase(Operator):
    bl_idname = "flight_case.delete"
    bl_label = "Delete Flight Case"
    bl_description = "Remove the active flight case and all its geometry"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case found.")
            return {"CANCELLED"}
        CaseManager.delete(root, context)
        self.report({"INFO"}, "Flight case deleted.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Preset operators
# ---------------------------------------------------------------------------

class FC_OT_SavePreset(Operator):
    bl_idname = "flight_case.save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current settings as a preset file"

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..presets.preset_manager import PresetManager
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        PresetManager.save(self.filepath, root)
        self.report({"INFO"}, f"Preset saved to {self.filepath}")
        return {"FINISHED"}


class FC_OT_LoadPreset(Operator):
    bl_idname = "flight_case.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load settings from a preset file"

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..presets.preset_manager import PresetManager
        from ..core.case_manager import CaseManager
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        PresetManager.load(self.filepath, root)
        CaseManager.update(root, context)
        self.report({"INFO"}, f"Preset loaded from {self.filepath}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Export operators
# ---------------------------------------------------------------------------

class FC_OT_ExportDXF(Operator):
    bl_idname = "flight_case.export_dxf"
    bl_label = "Export DXF"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.dxf")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import dxf_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        try:
            dxf_exporter.export(self.filepath, data)
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"DXF exported to {self.filepath}")
        return {"FINISHED"}


class FC_OT_ExportSVG(Operator):
    bl_idname = "flight_case.export_svg"
    bl_label = "Export SVG"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.svg")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import svg_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        svg_exporter.export(self.filepath, data)
        self.report({"INFO"}, f"SVG exported to {self.filepath}")
        return {"FINISHED"}


class FC_OT_ExportPDF(Operator):
    bl_idname = "flight_case.export_pdf"
    bl_label = "Export PDF"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.pdf")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import pdf_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        pdf_exporter.export(self.filepath, data)
        self.report({"INFO"}, f"PDF exported to {self.filepath}")
        return {"FINISHED"}


class FC_OT_ExportCSV(Operator):
    bl_idname = "flight_case.export_csv"
    bl_label = "Export CSV"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.csv")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import csv_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        csv_exporter.export(self.filepath, data)
        self.report({"INFO"}, "CSV exported.")
        return {"FINISHED"}


class FC_OT_ExportExcel(Operator):
    bl_idname = "flight_case.export_excel"
    bl_label = "Export Excel"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.xlsx")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import excel_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        try:
            excel_exporter.export(self.filepath, data)
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Excel exported to {self.filepath}")
        return {"FINISHED"}


class FC_OT_ExportSTL(Operator):
    bl_idname = "flight_case.export_stl"
    bl_label = "Export STL"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.stl")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import stl_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        stl_exporter.export(self.filepath, data, root)
        self.report({"INFO"}, f"STL exported to {self.filepath}")
        return {"FINISHED"}


class FC_OT_ExportSTEP(Operator):
    bl_idname = "flight_case.export_step"
    bl_label = "Export STEP"
    filepath: StringProperty(subtype="FILE_PATH", default="flight_case.step")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core.case_manager import CaseManager
        from ..export import step_exporter
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        data = CaseManager.build_case_data(root)
        step_exporter.export(self.filepath, data, root)
        self.report({"INFO"}, f"STEP exported to {self.filepath}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Drawing / View operators
# ---------------------------------------------------------------------------

class FC_OT_GenerateDrawings(Operator):
    bl_idname = "flight_case.generate_drawings"
    bl_label = "Generate Drawings"
    bl_description = "Create orthographic camera rigs for technical drawings"

    def execute(self, context):
        from ..drawings.drawing_generator import generate_drawings
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        generate_drawings(root, root.flight_case, context)
        self.report({"INFO"}, "Drawing cameras created.")
        return {"FINISHED"}


class FC_OT_ExplodedView(Operator):
    bl_idname = "flight_case.exploded_view"
    bl_label = "Toggle Exploded View"
    bl_description = "Explode or collapse the case components"

    def execute(self, context):
        from ..drawings.drawing_generator import generate_exploded_view, reset_exploded_view
        root = _active_case_root(context)
        if root is None:
            self.report({"WARNING"}, "No active flight case.")
            return {"CANCELLED"}
        if any("fc_exploded_offset" in child for child in root.children):
            reset_exploded_view(root)
            self.report({"INFO"}, "Exploded view reset.")
        else:
            generate_exploded_view(root, root.flight_case, context)
            self.report({"INFO"}, "Exploded view applied.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_CLASSES = [
    FC_OT_CreateFlightCase,
    FC_OT_UpdateFlightCase,
    FC_OT_DeleteFlightCase,
    FC_OT_SavePreset,
    FC_OT_LoadPreset,
    FC_OT_ExportDXF,
    FC_OT_ExportSVG,
    FC_OT_ExportPDF,
    FC_OT_ExportCSV,
    FC_OT_ExportExcel,
    FC_OT_ExportSTL,
    FC_OT_ExportSTEP,
    FC_OT_GenerateDrawings,
    FC_OT_ExplodedView,
]


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
