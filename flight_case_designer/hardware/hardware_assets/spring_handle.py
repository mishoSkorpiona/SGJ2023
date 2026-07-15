"""hardware/hardware_assets/spring_handle.py"""
from ..hardware_library import HardwareDefinition


def spring_handle_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="spring_handle",
        label="Spring Handle",
        width_mm=130.0,
        height_mm=40.0,
        depth_mm=30.0,
        rivet_spacing_mm=60.0,
        rivet_edge_offset_mm=15.0,
        offset_mm=0.0,
        mounting_faces=["front"],
        manufacturer="Penn Elcom",
        part_number="H1013",
    )
