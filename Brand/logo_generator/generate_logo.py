#!/usr/bin/env python3
"""
IsarPunk logo — Laughing Man badge:

  - LM teal (#057) + white
  - baseball cap + bill wordmark
  - eyes + flipped-eye smile
  - sun + river on the hat crown

Static: bilingual motto on the teal rim (EN top, DE bottom).
--animate: revolving ring motto.

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

LOGO_DIR = Path(__file__).resolve().parent.parent / "logo"


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
    """Compact sun for the hat crown — disc + triangular rays."""
    parts = [f'<g id="crown-sun" transform="translate({fmt(cx)} {fmt(cy)})">']
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
    # Black Circular Munich mark in the sun core
    cm_scale = (core_r * 1.136) / 50.0
    parts.append(
        f'<g id="cm-in-sun" transform="translate(0 0) scale({fmt(cm_scale)})" '
        f'fill="#B89A14" stroke="#B89A14">'
        f'<path d="M 41.997 18.712 A 45.979 45.979 0 1 1 42.321 -18.086" '
        f'fill="none" stroke-width="8.041" stroke-linecap="butt"/>'
        f'<circle cx="45.979" cy="0" r="4.021" stroke="none"/>'
        f'<path stroke="none" d="M -19.45 -16.94 L -19.45 17.32 L -11.811 17.32 '
        f'L -11.811 -3.189 L 0 16.938 L 11.811 -3.189 L 11.811 17.32 L 19.45 17.32 '
        f'L 19.45 -16.94 L 11.811 -16.94 L 0 4.333 L -11.811 -16.94 Z"/>'
        f'</g>'
    )
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
    """Wavy river stroke under the crown sun — sine ribbon."""
    pts: list[str] = []
    for i in range(samples + 1):
        t = i / samples
        x = cx - half_width + 2 * half_width * t
        envelope = math.sin(math.pi * t)
        y = cy + amp * envelope * math.sin(2 * math.pi * cycles * t)
        cmd = "M" if i == 0 else "L"
        pts.append(f"{cmd} {fmt(x)} {fmt(y)}")
    d = " ".join(pts)
    return (
        f'<path id="crown-river" d="{d}" fill="none" stroke="{stroke}" '
        f'stroke-width="{fmt(stroke_width)}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def motto_svg(*, animate: bool, motto: str) -> str:
    rim_r = 100.0
    # Bilingual EN top / DE bottom — same copy for static and animated.
    # Animated: whole rim-motto group rotates (matches circuit-animated).
    top_bottom = f'''<path id="rim-textpath-top" fill="none" d="M -{fmt(rim_r)},0 A {fmt(rim_r)} {fmt(rim_r)} 0 0 1 {fmt(rim_r)},0"/>
      <path id="rim-textpath-bottom" fill="none" d="M {fmt(rim_r)},0 A {fmt(rim_r)} {fmt(rim_r)} 0 0 1 -{fmt(rim_r)},0"/>
      <text fill="{WHITE}" font-size="13" font-weight="700" font-stretch="condensed"
            font-family="Impact, Haettenschweiler, Arial Narrow, sans-serif"
            letter-spacing="0.04em" text-anchor="middle">
        <textPath href="#rim-textpath-top" xlink:href="#rim-textpath-top" startOffset="50%">Hack your life / Save Oma</textPath>
      </text>
      <text fill="{WHITE}" font-size="13" font-weight="700" font-stretch="condensed"
            font-family="Impact, Haettenschweiler, Arial Narrow, sans-serif"
            letter-spacing="0.04em" text-anchor="middle">
        <textPath href="#rim-textpath-bottom" xlink:href="#rim-textpath-bottom" startOffset="50%">Hack dein Leben / Rette Oma</textPath>
      </text>'''
    if animate:
        return f'''<g id="rim-motto">
      <animateTransform attributeName="transform" type="rotate" from="360 0 0" to="0 0 0" dur="12s" repeatCount="indefinite"/>
      {top_bottom}
    </g>'''
    return f'''<g id="rim-motto">
      {top_bottom}
    </g>'''


def render_svg(*, animate: bool, motto: str) -> str:
    sun = crown_sun_svg()
    river = crown_river_svg(cy=-16.0)
    motto_block = motto_svg(animate=animate, motto=motto)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="-210 -170 380 340"
     role="img" aria-label="IsarPunk">
  <title>IsarPunk</title>
  <defs>
    <clipPath id="wordmark-glitch-top" clipPathUnits="userSpaceOnUse">
      <path d="M -162 8 H -78 L -78 23.4 L -88 23.1 L -96 23.6 L -104 22.9 L -112 23.8 L -116 21.2 L -120 24.4 L -126 22.5 L -134 23.8 L -142 22.7 L -150 23.6 L -162 23.2 Z"/>
    </clipPath>
    <clipPath id="wordmark-glitch-bot" clipPathUnits="userSpaceOnUse">
      <path d="M -162 40 H -78 L -78 23.4 L -88 23.1 L -96 23.6 L -104 22.9 L -112 23.8 L -116 21.2 L -120 24.4 L -126 22.5 L -134 23.8 L -142 22.7 L -150 23.6 L -162 23.2 Z"/>
    </clipPath>
  </defs>
  <g fill="{TEAL}">
    <!-- white ring (former outer motto track — kept as frame) -->
    <circle r="150" fill="{WHITE}"/>
    <circle r="115"/>
    <circle r="95" fill="{WHITE}"/>
    <!-- motto on the teal rim inside the cap/face circle -->
    {motto_block}
    <!-- bill tip disc (points left; lower than original LM) -->
    <circle cx="-160" cy="22" r="26"/>
    <!-- crown + bill -->
    <path d="M 95 8 V -4 H -160 A 26,26 0 0 0 -160 48 H -105 V 36 Z"/>
    <!-- sun + river on the hat crown -->
    <g id="crown-emblem">
      {sun}
      {river}
    </g>
    <!-- white bill highlight -->
    <path d="M 115 8 V 16 H 90 V 36 H -160 A 14,14 0 0 1 -160 8 Z" fill="{WHITE}"/>
    <!-- wordmark on the bill — jagged horizontal glitch -->
    <g id="bill-wordmark" fill="{TEAL}" font-size="16" font-weight="700"
       font-stretch="condensed" font-family="Impact, Haettenschweiler, Arial Narrow, sans-serif"
       letter-spacing="0.06em" text-anchor="middle" dominant-baseline="middle">
      <g clip-path="url(#wordmark-glitch-bot)">
        <text x="-120" y="24">IsarPunk</text>
      </g>
      <g clip-path="url(#wordmark-glitch-top)">
        <text x="-120" y="24" transform="translate(-0.9 0)">IsarPunk</text>
      </g>
    </g>
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
    parser = argparse.ArgumentParser(description="IsarPunk logo — LM base + crown sun/river")
    parser.add_argument(
        "--motto",
        default="IsarPunk · Hack your life · Save Oma",
        help="Revolving ring text (used with --animate)",
    )
    parser.add_argument("--animate", action="store_true", help="Spin the ring text")
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()

    out = args.output or LOGO_DIR / ("isarpunk-animated.svg" if args.animate else "isarpunk.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_svg(animate=args.animate, motto=args.motto), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
