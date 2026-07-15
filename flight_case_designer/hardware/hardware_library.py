"""
hardware/hardware_library.py — Registry of hardware item definitions.

A hardware definition provides:
  * name / label
  * bounding dimensions (width, height, depth in mm)
  * rivet pattern (spacing, edge offset)
  * placement offset from mounting surface
  * mounting face(s)
  * manufacturer / part number
  * parametric mesh builder (function that populates a BMesh)

New items are registered via HardwareLibrary.register() or loaded from JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import bmesh


@dataclass
class HardwareDefinition:
    """Data class describing a single hardware item."""

    name: str
    label: str
    width_mm: float = 50.0
    height_mm: float = 20.0
    depth_mm: float = 10.0
    rivet_spacing_mm: float = 50.0
    rivet_edge_offset_mm: float = 15.0
    offset_mm: float = 0.0          # offset from panel surface
    mounting_faces: List[str] = field(default_factory=lambda: ["front"])
    manufacturer: str = ""
    part_number: str = ""
    # Callable(bm: BMesh) → None  — populates the bmesh with hardware geometry
    mesh_builder: Optional[Callable] = field(default=None, repr=False)

    def build_mesh(self, bm: "bmesh.types.BMesh") -> None:
        """Populate *bm* with hardware geometry."""
        if self.mesh_builder is not None:
            self.mesh_builder(bm)
        else:
            _default_box_mesh(bm, self.width_mm, self.height_mm, self.depth_mm)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "width_mm": self.width_mm,
            "height_mm": self.height_mm,
            "depth_mm": self.depth_mm,
            "rivet_spacing_mm": self.rivet_spacing_mm,
            "rivet_edge_offset_mm": self.rivet_edge_offset_mm,
            "offset_mm": self.offset_mm,
            "mounting_faces": self.mounting_faces,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HardwareDefinition":
        return cls(
            name=data["name"],
            label=data.get("label", data["name"]),
            width_mm=data.get("width_mm", 50.0),
            height_mm=data.get("height_mm", 20.0),
            depth_mm=data.get("depth_mm", 10.0),
            rivet_spacing_mm=data.get("rivet_spacing_mm", 50.0),
            rivet_edge_offset_mm=data.get("rivet_edge_offset_mm", 15.0),
            offset_mm=data.get("offset_mm", 0.0),
            mounting_faces=data.get("mounting_faces", ["front"]),
            manufacturer=data.get("manufacturer", ""),
            part_number=data.get("part_number", ""),
        )


# ---------------------------------------------------------------------------
# Fallback box geometry
# ---------------------------------------------------------------------------

def _default_box_mesh(bm: "bmesh.types.BMesh", w_mm: float, h_mm: float, d_mm: float) -> None:
    w, h, d = w_mm / 1000, h_mm / 1000, d_mm / 1000
    hw, hh, hd = w / 2, h / 2, d / 2
    verts = [
        bm.verts.new((x, y, z))
        for x in (-hw, hw) for y in (-hd, hd) for z in (-hh, hh)
    ]
    faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    for fi in faces:
        bm.faces.new([verts[i] for i in fi])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


# ---------------------------------------------------------------------------
# Library class
# ---------------------------------------------------------------------------

class HardwareLibrary:
    """Registry for hardware definitions."""

    _items: Dict[str, HardwareDefinition] = {}

    @classmethod
    def _init_builtins(cls) -> None:
        from .hardware_assets.butterfly_latch import butterfly_latch_def
        from .hardware_assets.spring_handle import spring_handle_def
        from .hardware_assets.ball_corner import ball_corner_def
        from .hardware_assets.cast_corner import cast_corner_def
        from .hardware_assets.hinge import hinge_def
        from .hardware_assets.rubber_foot import rubber_foot_def
        from .hardware_assets.caster import caster_def
        from .hardware_assets.rack_rail import rack_rail_def

        for d in [
            butterfly_latch_def(),
            spring_handle_def(),
            ball_corner_def(),
            cast_corner_def(),
            hinge_def(),
            rubber_foot_def(),
            caster_def(),
            rack_rail_def(),
        ]:
            cls._items[d.name] = d

    @classmethod
    def get(cls, name: str) -> Optional[HardwareDefinition]:
        if not cls._items:
            cls._init_builtins()
        return cls._items.get(name)

    @classmethod
    def all_names(cls) -> List[str]:
        if not cls._items:
            cls._init_builtins()
        return list(cls._items.keys())

    @classmethod
    def register(cls, definition: HardwareDefinition) -> None:
        cls._items[definition.name] = definition

    @classmethod
    def load_from_json(cls, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        items = data if isinstance(data, list) else data.get("hardware", [])
        for item in items:
            cls.register(HardwareDefinition.from_dict(item))

    @classmethod
    def save_to_json(cls, filepath: str) -> None:
        data = [d.to_dict() for d in cls._items.values()]
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)


HardwareLibrary._init_builtins()
