# SPDX-License-Identifier: GPL-3.0-or-later
"""
Rivet generator.

Creates small cylinder objects representing blind pop-rivets along each
aluminium profile.  Rivets are spaced every ``rivet_spacing`` mm, starting
and ending ``rivet_edge_offset`` mm from each end of the profile run.

Rivet placement follows the same 12-edge + seam layout as the profiles.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple

import bpy
from mathutils import Vector

from .mesh_utils import create_cylinder, get_or_create_material, link_object

if TYPE_CHECKING:
    from .case_builder import CaseDimensions
    from ..properties import FCD_HardwareProperties


def _rivet_positions_along_edge(
    start: Vector,
    end: Vector,
    spacing: float,
    edge_offset: float,
) -> List[Vector]:
    """Return world positions of rivets spaced along an edge."""
    direction = end - start
    length    = direction.length
    if length < edge_offset * 2.0 + spacing:
        # Edge too short – place one rivet at midpoint
        return [start + direction * 0.5]

    norm = direction.normalized()
    positions: List[Vector] = []
    x = edge_offset
    while x <= length - edge_offset + 1e-6:
        positions.append(start + norm * x)
        x += spacing
    return positions


def generate_rivets(
    context:   bpy.types.Context,
    dims:      "CaseDimensions",
    hdw_props: "FCD_HardwareProperties",
    hw_col:    bpy.types.Collection,
) -> None:
    """Generate rivet cylinder objects along all profile edges."""

    mat = get_or_create_material(
        "FCD_Rivet",
        base_color=(0.85, 0.85, 0.85, 1.0),
        metallic=0.9,
        roughness=0.25,
    )

    r      = dims.rivet_diameter / 2.0
    depth  = dims.rivet_diameter * 0.6   # shallow dome
    space  = dims.rivet_spacing
    offset = dims.rivet_edge_offset
    t_in   = dims.prof_t

    w, d, h = dims.ext_w, dims.ext_d, dims.ext_h
    sz      = dims.split_z

    # Rivet edge definitions (same as profile edges)
    edges: List[Tuple[Vector, Vector]] = [
        # Bottom ring
        (Vector((t_in, t_in,     0)), Vector((w - t_in, t_in,     0))),
        (Vector((w-t_in, t_in,   0)), Vector((w - t_in, d - t_in, 0))),
        (Vector((w-t_in, d-t_in, 0)), Vector((t_in,     d - t_in, 0))),
        (Vector((t_in, d-t_in,   0)), Vector((t_in,     t_in,     0))),
        # Top ring
        (Vector((t_in, t_in,     h)), Vector((w - t_in, t_in,     h))),
        (Vector((w-t_in, t_in,   h)), Vector((w - t_in, d - t_in, h))),
        (Vector((w-t_in, d-t_in, h)), Vector((t_in,     d - t_in, h))),
        (Vector((t_in, d-t_in,   h)), Vector((t_in,     t_in,     h))),
        # Verticals (body)
        (Vector((t_in, t_in,     0)), Vector((t_in,     t_in,     sz))),
        (Vector((w-t_in, t_in,   0)), Vector((w - t_in, t_in,     sz))),
        (Vector((w-t_in, d-t_in, 0)), Vector((w - t_in, d - t_in, sz))),
        (Vector((t_in, d-t_in,   0)), Vector((t_in,     d - t_in, sz))),
        # Verticals (lid)
        (Vector((t_in, t_in,     sz)), Vector((t_in,     t_in,     h))),
        (Vector((w-t_in, t_in,   sz)), Vector((w - t_in, t_in,     h))),
        (Vector((w-t_in, d-t_in, sz)), Vector((w - t_in, d - t_in, h))),
        (Vector((t_in, d-t_in,   sz)), Vector((t_in,     d - t_in, h))),
        # Seam ring
        (Vector((t_in, t_in,     sz)), Vector((w - t_in, t_in,     sz))),
        (Vector((w-t_in, t_in,   sz)), Vector((w - t_in, d - t_in, sz))),
        (Vector((w-t_in, d-t_in, sz)), Vector((t_in,     d - t_in, sz))),
        (Vector((t_in, d-t_in,   sz)), Vector((t_in,     t_in,     sz))),
    ]

    counter = 0
    for start, end in edges:
        positions = _rivet_positions_along_edge(start, end, space, offset)
        for pos in positions:
            obj = create_cylinder(
                f"Rivet_{counter:04d}",
                radius=r,
                depth=depth,
                segments=8,
                location=pos,
                material=mat,
            )
            link_object(obj, hw_col)
            counter += 1
