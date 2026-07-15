# SPDX-License-Identifier: GPL-3.0-or-later
"""
Blender operators for the Flight Case Designer.

All operators live in the ``fcd`` namespace (bl_idname prefix ``fcd.*``).

Operator list
-------------
FCD_OT_create_case      – Create a brand-new flight case from scene properties.
FCD_OT_rebuild_case     – Rebuild the active case (triggered by property updates).
FCD_OT_clear_case       – Delete all case objects and collections.
FCD_OT_export_bom       – Write cut-list / BOM CSV files to disk.
FCD_OT_save_preset      – Save current settings as a named preset (JSON).
FCD_OT_load_preset      – Load a preset JSON file into the scene properties.
FCD_OT_add_hardware     – (Future) Add a custom hardware item to the catalog.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Shared rebuild helper
# ---------------------------------------------------------------------------

def _do_build(context: bpy.types.Context) -> set:
    """
    Core rebuild function invoked by both Create and Rebuild operators.
    Returns ``{'FINISHED'}`` on success or ``{'CANCELLED'}`` on error.
    """
    props = context.scene.fcd
    case  = props.case
    case_name = case.case_name or "Flight Case"

    from .generators.case_builder import CaseDimensions
    from .generators.mesh_utils import (
        get_or_create_root_collection,
        ensure_collection,
        clear_collection,
        link_object,
    )
    from .generators.panel_gen   import generate_panels
    from .generators.profile_gen import generate_profiles
    from .generators.hardware_gen import generate_hardware
    from .generators.foam_gen    import generate_foam
    from .generators.rivet_gen   import generate_rivets

    # Compute all dimensions
    dims = CaseDimensions(props)

    # Root and sub-collections
    root_col     = get_or_create_root_collection(case_name)
    body_col     = ensure_collection(root_col, f"{case_name}_Body")
    lid_col      = ensure_collection(root_col, f"{case_name}_Lid")
    profiles_col = ensure_collection(root_col, f"{case_name}_Profiles")
    hardware_col = ensure_collection(root_col, f"{case_name}_Hardware")
    foam_col     = ensure_collection(root_col, f"{case_name}_Foam")

    # Clear previous geometry
    for col in (body_col, lid_col, profiles_col, hardware_col, foam_col):
        clear_collection(col)

    # ---------- Panels ----------
    generate_panels(context, dims, case, body_col, lid_col)

    # ---------- Profiles ----------
    if case.show_profiles:
        generate_profiles(context, dims, case, profiles_col)

    # ---------- Hardware ----------
    if case.show_hardware:
        generate_hardware(
            context, dims,
            props.equipment, case, props.hardware,
            hardware_col,
        )

    # ---------- Foam ----------
    if case.show_foam:
        generate_foam(
            context, dims,
            props.equipment, case, props.foam,
            foam_col,
        )

    # ---------- Rivets ----------
    if props.hardware.show_rivets:
        generate_rivets(context, dims, props.hardware, hardware_col)

    # ---------- Equipment ghost ----------
    if case.show_equipment:
        _make_equipment_ghost(context, dims, props, root_col)

    # Tag the root collection so we can find it later
    root_col["fcd_case_name"] = case_name

    return {"FINISHED"}


def _make_equipment_ghost(context, dims, props, root_col):
    """Transparent bounding-box ghost showing the equipment envelope."""
    from .generators.mesh_utils import create_box_mesh, get_or_create_material, link_object

    col_name = f"{props.case.case_name}_Equipment"
    from .generators.mesh_utils import ensure_collection
    eq_col = ensure_collection(root_col, col_name)
    from .generators.mesh_utils import clear_collection
    clear_collection(eq_col)

    mat = get_or_create_material(
        "FCD_Equipment_Ghost",
        base_color=(0.8, 0.4, 0.1, 0.25),
        roughness=0.5,
        alpha=0.25,
    )

    t  = dims.ply_t
    x0 = t + dims.foam_l
    y0 = t + dims.foam_f
    z0 = t + dims.foam_b

    obj = create_box_mesh(
        "Equipment_Ghost",
        dims.eq_w, dims.eq_d, dims.eq_h,
        location=(x0, y0, z0),
        material=mat,
    )
    obj.display_type = "WIRE"
    link_object(obj, eq_col)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class FCD_OT_create_case(Operator):
    """Create a new flight case from the current scene property settings."""

    bl_idname  = "fcd.create_case"
    bl_label   = "Create Flight Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set:
        return _do_build(context)

    def invoke(self, context, event):
        return self.execute(context)


class FCD_OT_rebuild_case(Operator):
    """Rebuild the flight case geometry (called automatically on property change)."""

    bl_idname  = "fcd.rebuild_case"
    bl_label   = "Rebuild Flight Case"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        return _do_build(context)


class FCD_OT_clear_case(Operator):
    """Delete all flight case geometry and collections from the scene."""

    bl_idname  = "fcd.clear_case"
    bl_label   = "Clear Flight Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set:
        case_name = context.scene.fcd.case.case_name or "Flight Case"
        if case_name in bpy.data.collections:
            from .generators.mesh_utils import clear_collection
            root_col = bpy.data.collections[case_name]
            clear_collection(root_col)
            # Remove child collections
            for child in list(root_col.children):
                bpy.data.collections.remove(child, do_unlink=True)
            bpy.data.collections.remove(root_col, do_unlink=True)
            self.report({"INFO"}, f"Cleared case '{case_name}'.")
        else:
            self.report({"WARNING"}, f"No case collection named '{case_name}' found.")
        return {"FINISHED"}


class FCD_OT_export_bom(Operator):
    """Export cut list and bill of materials to CSV files."""

    bl_idname = "fcd.export_bom"
    bl_label  = "Export BOM / Cut List"

    def execute(self, context: bpy.types.Context) -> set:
        props = context.scene.fcd
        from .generators.case_builder import CaseDimensions
        from .exporters.bom_exporter  import export_manufacturing_files

        dims    = CaseDimensions(props)
        written = export_manufacturing_files(props, dims)

        self.report(
            {"INFO"},
            f"Exported {len(written)} files to "
            f"{bpy.path.abspath(props.manufacturing.export_path)}",
        )
        return {"FINISHED"}


class FCD_OT_save_preset(Operator):
    """Save the current settings as a JSON preset file."""

    bl_idname  = "fcd.save_preset"
    bl_label   = "Save Preset"
    bl_options = {"REGISTER"}

    filepath: StringProperty(
        name="File Path",
        description="Where to save the preset JSON file",
        subtype="FILE_PATH",
        default="//flight_case_preset.json",
    )
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context: bpy.types.Context) -> set:
        props = context.scene.fcd
        data  = _props_to_dict(props)
        path  = bpy.path.abspath(self.filepath)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
        self.report({"INFO"}, f"Preset saved to {path}")
        return {"FINISHED"}


class FCD_OT_load_preset(Operator):
    """Load a preset JSON file into the scene properties."""

    bl_idname  = "fcd.load_preset"
    bl_label   = "Load Preset"
    bl_options = {"REGISTER", "UNDO"}

    filepath: StringProperty(
        name="File Path",
        description="Preset JSON file to load",
        subtype="FILE_PATH",
        default="//",
    )
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context: bpy.types.Context) -> set:
        path = bpy.path.abspath(self.filepath)
        if not os.path.isfile(path):
            self.report({"ERROR"}, f"File not found: {path}")
            return {"CANCELLED"}
        with open(path) as fh:
            data = json.load(fh)
        _dict_to_props(data, context.scene.fcd)
        self.report({"INFO"}, f"Preset loaded from {path}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Preset serialisation helpers
# ---------------------------------------------------------------------------

def _props_to_dict(props) -> dict:
    """Serialise FCD_SceneProperties to a plain dict (JSON-compatible)."""
    def _group(pg) -> dict:
        out = {}
        for key in pg.bl_rna.properties.keys():
            if key in ("rna_type", "name"):
                continue
            val = getattr(pg, key)
            if isinstance(val, str):
                out[key] = val
            elif isinstance(val, (int, float, bool)):
                out[key] = val
        return out

    return {
        "equipment":     _group(props.equipment),
        "case":          _group(props.case),
        "foam":          _group(props.foam),
        "hardware":      _group(props.hardware),
        "manufacturing": _group(props.manufacturing),
    }


def _dict_to_props(data: dict, props) -> None:
    """Deserialise a plain dict into FCD_SceneProperties."""
    def _apply(pg, src: dict):
        for key, val in src.items():
            try:
                setattr(pg, key, val)
            except (AttributeError, TypeError):
                pass

    for group_name in ("equipment", "case", "foam", "hardware", "manufacturing"):
        if group_name in data:
            _apply(getattr(props, group_name), data[group_name])


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_CLASSES = [
    FCD_OT_create_case,
    FCD_OT_rebuild_case,
    FCD_OT_clear_case,
    FCD_OT_export_bom,
    FCD_OT_save_preset,
    FCD_OT_load_preset,
]


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
