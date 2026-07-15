"""ui/panels/foam_panel.py — Foam settings panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_foam(Panel):
    bl_label = "Foam"
    bl_idname = "VIEW3D_PT_flight_case_foam"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return
        foam = obj.flight_case.foam
        layout.prop(foam, "foam_type")
        layout.prop(foam, "density")
        layout.prop(foam, "compression")
        layout.separator()
        layout.prop(foam, "asymmetric")
        if foam.asymmetric:
            col = layout.column(align=True)
            col.prop(foam, "top",    text="Top (mm)")
            col.prop(foam, "bottom", text="Bottom (mm)")
            col.prop(foam, "front",  text="Front (mm)")
            col.prop(foam, "back",   text="Back (mm)")
            col.prop(foam, "left",   text="Left (mm)")
            col.prop(foam, "right",  text="Right (mm)")
        else:
            layout.prop(foam, "bottom", text="Thickness (mm)")
        layout.separator()
        layout.prop(foam, "finger_pulls")
        layout.prop(foam, "cable_channels")
        layout.prop(foam, "multi_layer")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_foam)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_foam)
