"""ui/panels/equipment_panel.py — Equipment settings panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_equipment(Panel):
    bl_label = "Equipment"
    bl_idname = "VIEW3D_PT_flight_case_equipment"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return
        eq = obj.flight_case.equipment
        col = layout.column(align=True)
        col.prop(eq, "width",  text="Width (mm)")
        col.prop(eq, "depth",  text="Depth (mm)")
        col.prop(eq, "height", text="Height (mm)")
        col.prop(eq, "weight", text="Weight (kg)")
        layout.prop(eq, "orientation")
        layout.separator()
        col2 = layout.column(align=True)
        col2.prop(eq, "cable_clearance",    text="Cable Clearance (mm)")
        col2.prop(eq, "connector_clearance",text="Connector Clearance (mm)")
        col2.prop(eq, "internal_clearance", text="Internal Clearance (mm)")
        col2.prop(eq, "air_gap",            text="Air Gap (mm)")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_equipment)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_equipment)
