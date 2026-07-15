"""ui/panels/export_panel.py — Export panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_export(Panel):
    bl_label = "Export"
    bl_idname = "VIEW3D_PT_flight_case_export"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 8

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="2D Drawings:")
        col.operator("flight_case.export_dxf",  icon="EXPORT")
        col.operator("flight_case.export_svg",  icon="EXPORT")
        col.operator("flight_case.export_pdf",  icon="EXPORT")
        col.separator()
        col.label(text="Bill of Materials:")
        col.operator("flight_case.export_csv",   icon="EXPORT")
        col.operator("flight_case.export_excel", icon="EXPORT")
        col.separator()
        col.label(text="3D Geometry:")
        col.operator("flight_case.export_stl",  icon="EXPORT")
        col.operator("flight_case.export_step", icon="EXPORT")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_export)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_export)
