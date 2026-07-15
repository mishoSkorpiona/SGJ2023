"""hardware/hardware_assets/rubber_foot.py"""
from ..hardware_library import HardwareDefinition


def rubber_foot_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="rubber_foot",
        label="Rubber Foot",
        width_mm=35.0,
        height_mm=20.0,
        depth_mm=35.0,
        rivet_spacing_mm=0.0,
        rivet_edge_offset_mm=0.0,
        offset_mm=0.0,
        mounting_faces=["bottom"],
        manufacturer="Penn Elcom",
        part_number="F0040",
    )
