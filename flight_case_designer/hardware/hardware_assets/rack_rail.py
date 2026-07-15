"""hardware/hardware_assets/rack_rail.py"""
from ..hardware_library import HardwareDefinition


def rack_rail_def() -> HardwareDefinition:
    return HardwareDefinition(
        name="rack_rail",
        label="Rack Rail",
        width_mm=20.0,
        height_mm=44.45,
        depth_mm=5.0,
        rivet_spacing_mm=44.45,
        rivet_edge_offset_mm=10.0,
        offset_mm=0.0,
        mounting_faces=["left", "right"],
        manufacturer="Penn Elcom",
        part_number="R0932",
    )
