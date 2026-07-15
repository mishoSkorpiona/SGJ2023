"""ui/panels/case_panel.py — Case type and material panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_case(Panel):
    bl_label = "Case"
    bl_idname = "VIEW3D_PT_flight_case_case"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return
        params = obj.flight_case
        layout.prop(params, "case_type")
        if params.case_type == "RACK_CASE":
            layout.prop(params, "rack_units")
        layout.separator()
        mat = params.material
        layout.prop(mat, "plywood_type")
        layout.prop(mat, "plywood_thickness")
        if mat.plywood_thickness == "0":
            layout.prop(mat, "plywood_thickness_custom")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_case)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_case)
