"""hardware/hardware_assets/hinge.py"""
from ..hardware_library import HardwareDefinition


def hinge_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="hinge",
        label="Hinge",
        width_mm=50.0,
        height_mm=25.0,
        depth_mm=6.0,
        rivet_spacing_mm=20.0,
        rivet_edge_offset_mm=8.0,
        offset_mm=0.0,
        mounting_faces=["back"],
        manufacturer="Penn Elcom",
        part_number="H1034",
    )
