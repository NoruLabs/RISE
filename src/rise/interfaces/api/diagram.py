"""Nozzle cross-section SVG generator — presentation layer only.

build_nozzle_svg() is a pure function: takes geometry, returns an SVG string.
No I/O, no domain logic, no side effects.
"""
from __future__ import annotations

import math

from rise.domain.services.geometry_service import GeometryResult

# Fixed viewBox so all diagrams have consistent scale
_VB_W = 600
_VB_H = 220


def build_nozzle_svg(geometry: GeometryResult) -> str:  # noqa: PLR0914
    """Return an SVG string representing the nozzle cross-section.

    All dimensions are proportional to real values, scaled to fit the viewBox.
    """
    g = geometry

    total_length = g.chamber_length_m + g.converging_length_m + g.diverging_length_m
    max_radius = g.chamber_diameter_m / 2.0

    # Scale factors: map physical space to SVG pixels
    margin_x = 40.0
    margin_y = 20.0
    draw_w = _VB_W - 2 * margin_x
    draw_h = _VB_H - 2 * margin_y

    sx = draw_w / total_length if total_length > 0 else 1.0
    sy = (draw_h / 2.0) / max_radius if max_radius > 0 else 1.0
    cx = _VB_W / 2.0
    cy = _VB_H / 2.0  # centerline

    def px(length_m: float) -> float:
        return margin_x + length_m * sx

    def pr(radius_m: float) -> float:
        return radius_m * sy

    # Key x positions
    x_chamber_start = px(0)
    x_conv_start = px(g.chamber_length_m)
    x_throat = px(g.chamber_length_m + g.converging_length_m)
    x_exit = px(total_length)

    r_chamber = pr(g.chamber_diameter_m / 2.0)
    r_throat = pr(g.throat_diameter_m / 2.0)
    r_exit = pr(g.exit_diameter_m / 2.0)

    # Upper profile: chamber wall → converging cone → throat → diverging cone
    # Lower profile is mirrored
    path_upper = (
        f"M {x_chamber_start:.1f} {cy - r_chamber:.1f} "
        f"H {x_conv_start:.1f} "
        f"L {x_throat:.1f} {cy - r_throat:.1f} "
        f"L {x_exit:.1f} {cy - r_exit:.1f}"
    )
    path_lower = (
        f"M {x_chamber_start:.1f} {cy + r_chamber:.1f} "
        f"H {x_conv_start:.1f} "
        f"L {x_throat:.1f} {cy + r_throat:.1f} "
        f"L {x_exit:.1f} {cy + r_exit:.1f}"
    )

    # Chamber end cap
    cap = (
        f"M {x_chamber_start:.1f} {cy - r_chamber:.1f} "
        f"V {cy + r_chamber:.1f}"
    )

    # Exit plane
    exit_line = (
        f"M {x_exit:.1f} {cy - r_exit:.1f} "
        f"V {cy + r_exit:.1f}"
    )

    # Throat marker (vertical dashed)
    throat_marker = (
        f"M {x_throat:.1f} {cy - r_throat - 12:.1f} "
        f"V {cy + r_throat + 12:.1f}"
    )

    # Dimension labels
    def label(x: float, y: float, text: str, anchor: str = "middle") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="9" fill="#94a3b8">{text}</text>'

    def dim_line(x1: float, y1: float, x2: float, y2: float) -> str:
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#475569" stroke-width="0.5" stroke-dasharray="2,2"/>'

    labels_svg = [
        label(x_throat, cy + r_throat + 22, f"Øt {g.throat_diameter_m*1000:.1f} mm"),
        label(x_exit + 8, cy, f"Øe {g.exit_diameter_m*1000:.1f} mm", "start"),
        label(x_chamber_start + (x_conv_start - x_chamber_start) / 2, cy - r_chamber - 6,
              f"Lc {g.chamber_length_m*1000:.1f} mm"),
        dim_line(x_throat, cy - r_throat, x_throat, cy - r_throat - 10),
        dim_line(x_throat, cy + r_throat, x_throat, cy + r_throat + 14),
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_VB_W} {_VB_H}" width="100%" style="max-height:200px">
  <rect width="{_VB_W}" height="{_VB_H}" fill="#0f1117"/>
  <!-- Centerline -->
  <line x1="{x_chamber_start:.1f}" y1="{cy:.1f}" x2="{x_exit:.1f}" y2="{cy:.1f}"
        stroke="#334155" stroke-width="0.75" stroke-dasharray="4,3"/>
  <!-- Throat dashed marker -->
  <path d="{throat_marker}" stroke="#7c3aed" stroke-width="0.75" stroke-dasharray="3,3" fill="none"/>
  <!-- Nozzle walls (upper + lower) -->
  <path d="{path_upper}" stroke="#a78bfa" stroke-width="1.5" fill="none"/>
  <path d="{path_lower}" stroke="#a78bfa" stroke-width="1.5" fill="none"/>
  <!-- Fill interior -->
  <path d="{path_upper} L {x_exit:.1f} {cy + r_exit:.1f} {path_lower[2:]} Z"
        fill="#a78bfa" opacity="0.05"/>
  <!-- End cap and exit plane -->
  <path d="{cap}" stroke="#a78bfa" stroke-width="1.5" fill="none"/>
  <path d="{exit_line}" stroke="#64748b" stroke-width="1" fill="none" stroke-dasharray="3,2"/>
  {''.join(labels_svg)}
</svg>"""
    return svg
