"""ui/panels/profiles_panel.py — Aluminium profile selection panel."""
import bpy
from bpy.types import Panel
from ..sidebar import SIDEBAR_CATEGORY, SIDEBAR_SPACE, SIDEBAR_REGION


class VIEW3D_PT_flight_case_profiles(Panel):
    bl_label = "Profiles"
    bl_idname = "VIEW3D_PT_flight_case_profiles"
    bl_space_type = SIDEBAR_SPACE
    bl_region_type = SIDEBAR_REGION
    bl_category = SIDEBAR_CATEGORY
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is None or "flight_case_root" not in obj:
            layout.label(text="No active flight case.", icon="INFO")
            return
        profile = obj.flight_case.profile
        layout.prop(profile, "profile_type")
        if profile.profile_type == "CUSTOM" or profile.custom_profile_name:
            layout.prop(profile, "custom_profile_name")


def register():
    bpy.utils.register_class(VIEW3D_PT_flight_case_profiles)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_flight_case_profiles)
