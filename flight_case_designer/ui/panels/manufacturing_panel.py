"""ui/panels/manufacturing_panel.py — Manufacturing summary panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_manufacturing(Panel):
    bl_label = "Manufacturing"
    bl_idname = "VIEW3D_PT_flight_case_manufacturing"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 7

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return

        from ...core.case_manager import CaseManager
        from ...manufacturing.cost import estimate_cost

        try:
            data = CaseManager.build_case_data(obj)
            estimate_cost(data)
        except Exception:
            layout.label(text="Generate case to see summary.")
            return

        box = layout.box()
        box.label(text="External Dimensions (mm):")
        row = box.row()
        row.label(text=f"W: {data.ext_width:.1f}")
        row.label(text=f"D: {data.ext_depth:.1f}")
        row.label(text=f"H: {data.ext_height:.1f}")

        layout.label(text=f"Panels:   {len(data.panels)}")
        layout.label(text=f"Hardware: {sum(h['count'] for h in data.hardware_items)}")
        layout.label(text=f"Total Weight: {data.total_weight:.2f} kg")
        layout.label(text=f"Est. Cost:    {data.total_cost:.2f}")

        layout.operator("flight_case.generate_drawings", icon="CAMERA_DATA")
        layout.operator("flight_case.exploded_view", icon="OUTLINER_OB_EMPTY")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_manufacturing)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_manufacturing)
