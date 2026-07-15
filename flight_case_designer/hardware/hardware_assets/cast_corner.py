"""hardware/hardware_assets/cast_corner.py"""
from ..hardware_library import HardwareDefinition


def cast_corner_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="cast_corner",
        label="Cast Corner",
        width_mm=52.0,
        height_mm=52.0,
        depth_mm=52.0,
        rivet_spacing_mm=20.0,
        rivet_edge_offset_mm=8.0,
        offset_mm=0.0,
        mounting_faces=["corner"],
        manufacturer="Penn Elcom",
        part_number="C1137",
    )
