"""ui/panels/hardware_panel.py — Hardware selection panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_hardware(Panel):
    bl_label = "Hardware"
    bl_idname = "VIEW3D_PT_flight_case_hardware"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return
        hw = obj.flight_case.hardware
        layout.prop(hw, "auto_placement")
        layout.separator()
        col = layout.column(align=True)
        col.prop(hw, "butterfly_latches")
        col.prop(hw, "spring_handles")
        col.prop(hw, "ball_corners")
        col.prop(hw, "cast_corners")
        col.prop(hw, "hinges")
        col.prop(hw, "rubber_feet")
        col.prop(hw, "casters")
        col.prop(hw, "rack_rails")
        col.prop(hw, "stacking_cups")
        col.prop(hw, "label_holders")
        layout.separator()
        rv = obj.flight_case.rivet
        layout.label(text="Rivet Settings:")
        col2 = layout.column(align=True)
        col2.prop(rv, "spacing",      text="Spacing (mm)")
        col2.prop(rv, "edge_offset",  text="Edge Offset (mm)")
        col2.prop(rv, "diameter",     text="Diameter (mm)")
        col2.prop(rv, "corner_skip")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_hardware)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_hardware)
