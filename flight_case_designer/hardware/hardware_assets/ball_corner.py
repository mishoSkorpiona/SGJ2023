"""hardware/hardware_assets/ball_corner.py"""
from ..hardware_library import HardwareDefinition


def ball_corner_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="ball_corner",
        label="Ball Corner",
        width_mm=46.0,
        height_mm=46.0,
        depth_mm=46.0,
        rivet_spacing_mm=20.0,
        rivet_edge_offset_mm=8.0,
        offset_mm=0.0,
        mounting_faces=["corner"],
        manufacturer="Penn Elcom",
        part_number="C1072",
    )
