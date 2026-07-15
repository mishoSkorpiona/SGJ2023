"""hardware/hardware_assets/caster.py"""
from ..hardware_library import HardwareDefinition


def caster_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="caster",
        label="Caster / Wheel",
        width_mm=75.0,
        height_mm=85.0,
        depth_mm=75.0,
        rivet_spacing_mm=0.0,
        rivet_edge_offset_mm=0.0,
        offset_mm=0.0,
        mounting_faces=["bottom"],
        manufacturer="Penn Elcom",
        part_number="R0740",
    )
