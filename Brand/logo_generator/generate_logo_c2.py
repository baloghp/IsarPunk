#!/usr/bin/env python3
"""
IsarPunk logo — Concept 2

Laughing Man badge base:
  - LM teal (#057) + white
  - baseball cap + bill wordmark
  - eyes + flipped-eye smile
  - fresh sun + river drawn on the hat crown (not from concept 1)

Outer ring + revolving motto kept but hidden.
Stdlib only.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


TEAL = "#005577"
WHITE = "#FFFFFF"
SUN = "#F5D400"
RIVER = "#5EC8E8"


def fmt(n: float) -> str:
    s = f"{n:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def crown_sun_svg(
    *,
    cx: float = 0.0,
    cy: float = -52.0,
    core_r: float = 11.0,
    ray_inner: float = 13.0,
    ray_outer: float = 26.0,
    ray_count: int = 8,
    ray_base_deg: float = 28.0,
    fill: str = SUN,
) -> str:
    """Compact sun for the hat crown — disc + triangular rays (computed fresh)."""
    parts = [f'<g id="crown-sun" transform="translate({fmt(cx)} {fmt(cy)})">']
    # Rays first; disc on top for clean join
    for i in range(ray_count):
        mid = -90.0 + i * (360.0 / ray_count)
        half = ray_base_deg / 2.0
        a = polar(0, 0, ray_inner, mid - half)
        tip = polar(0, 0, ray_outer, mid)
        b = polar(0, 0, ray_inner, mid + half)
        parts.append(
            f'<polygon fill="{fill}" points="'
            f'{fmt(a[0])},{fmt(a[1])} {fmt(tip[0])},{fmt(tip[1])} {fmt(b[0])},{fmt(b[1])}"/>'
        )
    parts.append(f'<circle r="{fmt(core_r)}" fill="{fill}"/>')
    parts.append("</g>")
    return "\n      ".join(parts)


def crown_river_svg(
    *,
    cx: float = 0.0,
    cy: float = -28.0,
    half_width: float = 48.0,
    amp: float = 5.0,
    cycles: float = 2.0,
    samples: int = 40,
    stroke: str = RIVER,
    stroke_width: float = 4.0,
) -> str:
    """Wavy river stroke under the crown sun — sine ribbon, computed fresh."""
    pts: list[str] = []
    for i in range(samples + 1):
        t = i / samples
        x = cx - half_width + 2 * half_width * t
        envelope = math.sin(math.pi * t)  # fade at ends
        y = cy + amp * envelope * math.sin(2 * math.pi * cycles * t)
        cmd = "M" if i == 0 else "L"
        pts.append(f"{cmd} {fmt(x)} {fmt(y)}")
    d = " ".join(pts)
    return (
        f'<path id="crown-river" d="{d}" fill="none" stroke="{stroke}" '
        f'stroke-width="{fmt(stroke_width)}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def render_svg(*, animate: bool, motto: str) -> str:
    # Motto runs on the teal rim between face (r=95) and cap disc (r=115)
    rim_r = 100.0
    text_path = (
        f"M {fmt(rim_r)},0 "
        f"A {fmt(rim_r)} {fmt(rim_r)} 0 0 1 -{fmt(rim_r)},0 "
        f"A {fmt(rim_r)} {fmt(rim_r)} 0 0 1 {fmt(rim_r)},0"
    )
    ring = f"{motto}   ·   {motto}   ·   "

    anim = ""
    if animate:
        anim = (
            '<animateTransform attributeName="transform" type="rotate" '
            'from="360 0 0" to="0 0 0" dur="12s" repeatCount="indefinite"/>'
        )

    sun = crown_sun_svg()
    river = crown_river_svg(cy=-16.0)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="-210 -170 380 340"
     role="img" aria-label="IsarPunk Concept 2">
  <title>IsarPunk — Concept 2</title>
  <g fill="{TEAL}">
    <!-- white ring (former outer motto track — kept as frame) -->
    <circle r="150" fill="{WHITE}"/>
    <circle r="115"/>
    <circle r="95" fill="{WHITE}"/>
    <!-- motto on the teal rim inside the cap/face circle -->
    <g id="rim-motto">
      <path id="c2-textpath" fill="none" d="{text_path}"/>
      <text fill="{WHITE}" font-size="13" font-weight="700" font-stretch="condensed"
            font-family="Impact, Haettenschweiler, Arial Narrow, sans-serif"
            letter-spacing="0.04em">
        {anim}
        <textPath href="#c2-textpath" xlink:href="#c2-textpath">{ring}</textPath>
      </text>
    </g>
    <!-- bill tip disc (points left; lower than original LM) -->
    <circle cx="-160" cy="22" r="26"/>
    <!-- crown + bill -->
    <path d="M 95 8 V -4 H -160 A 26,26 0 0 0 -160 48 H -105 V 36 Z"/>
    <!-- sun + river on the hat crown (drawn fresh for c2) -->
    <g id="crown-emblem">
      {sun}
      {river}
    </g>
    <!-- white bill highlight -->
    <path d="M 115 8 V 16 H 90 V 36 H -160 A 14,14 0 0 1 -160 8 Z" fill="{WHITE}"/>
    <!-- wordmark on the bill -->
    <text id="bill-wordmark" x="-120" y="24" fill="{TEAL}" font-size="16" font-weight="700"
          font-stretch="condensed" font-family="Impact, Haettenschweiler, Arial Narrow, sans-serif"
          letter-spacing="0.06em" text-anchor="middle" dominant-baseline="middle">IsarPunk</text>
    <!-- eyes (lowered with the bill) -->
    <path d="M -20 34 C -37 20 -47 20 -64 34 C -58 9 -27 9 -20 34 Z"/>
    <path d="M 60 34 C 43 20 33 20 16 34 C 22 9 53 9 60 34 Z"/>
    <!-- smile: exact same eye geometry, upside-down, between the eyes, lower -->
    <g id="smile" transform="translate(-2 64) scale(1 -1) translate(42 -21.5)">
      <path d="M -20 34 C -37 20 -47 20 -64 34 C -58 9 -27 9 -20 34 Z"/>
    </g>
  </g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="IsarPunk Concept 2 — LM base + crown sun/river")
    parser.add_argument(
        "--motto",
        default="IsarPunk · Hack your life · Save Oma",
        help="Ring text",
    )
    parser.add_argument("--animate", action="store_true", help="Spin the ring text")
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()

    out = args.output or (
        Path(__file__).resolve().parent.parent / "logo" / "concept2" / "isarpunk-c2.svg"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_svg(animate=args.animate, motto=args.motto), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
