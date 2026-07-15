"""ui/panels/project_panel.py — Project section panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_project(Panel):
    bl_label = "Project"
    bl_idname = "VIEW3D_PT_flight_case_project"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        layout.operator("flight_case.create", icon="ADD")
        layout.operator("flight_case.update", icon="FILE_REFRESH")
        layout.operator("flight_case.delete", icon="TRASH")
        layout.separator()
        layout.operator("flight_case.save_preset", icon="FILE_TICK")
        layout.operator("flight_case.load_preset", icon="FILEBROWSER")

        obj = context.object
        if obj and "flight_case_root" in obj:
            layout.separator()
            layout.prop(obj.flight_case, "project_name", text="Project Name")
            warnings = obj.get("flight_case_warnings", [])
            if warnings:
                box = layout.box()
                box.label(text=f"{len(warnings)} collision warning(s):", icon="ERROR")
                for w in warnings[:5]:
                    box.label(text=w, icon="DOT")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_project)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_project)
