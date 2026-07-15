"""ui/panels/panels_panel.py — Panel / plywood overview."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_panels(Panel):
    bl_label = "Panels"
    bl_idname = "VIEW3D_PT_flight_case_panels"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 6

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return

        col_name = obj.flight_case.project_name + "_Panels"
        if col_name not in bpy.data.collections:
            layout.label(text="No panels generated yet.")
            return

        col = bpy.data.collections[col_name]
        for panel_obj in col.objects:
            row = layout.row()
            row.label(text=panel_obj.name, icon="MESH_PLANE")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_panels)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_panels)
