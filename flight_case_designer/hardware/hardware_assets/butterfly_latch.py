"""hardware/hardware_assets/butterfly_latch.py"""
from ..hardware_library import HardwareDefinition


def butterfly_latch_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="butterfly_latch",
        label="Butterfly Latch",
        width_mm=62.0,
        height_mm=25.0,
        depth_mm=8.0,
        rivet_spacing_mm=45.0,
        rivet_edge_offset_mm=10.0,
        offset_mm=0.0,
        mounting_faces=["front", "back"],
        manufacturer="Penn Elcom",
        part_number="E0337",
    )
