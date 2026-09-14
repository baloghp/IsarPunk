#!/usr/bin/env python3
"""
IsarPunk logo geometry → SVG

Sun/gear rays (deck jacket patch) around the Electronics Circle **CM**
monogram as the core. Optional Isar river curve + wordmark lockup.
Stdlib only.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


# Palette pulled from presentation jacket / holograms
YELLOW = "#F5D400"
PURPLE = "#4B2A8A"
CYAN = "#5EC8E8"
INK = "#1A1228"
WHITE = "#FFFFFF"
SUN = "#F5D400"  # sun-ray yellow (same family as jacket)


Point = tuple[float, float]


@dataclass(frozen=True)
class CMParams:
    """
    Electronics Circle center mark: open C, geometric M, gap dot.
    Fitted inside a disc of radius `disc_radius` (the white CM circle).
    """

    disc_radius: float = 30.0
    # C = thick open ring; gap centered at 0° (3 o'clock), like the CM badge
    c_outer: float = 24.0
    c_inner: float = 16.5
    gap_deg: float = 52.0
    # Dot sits in the middle of the C gap
    dot_radius: float = 2.8
    # M stroke geometry (unit-ish, scaled to fit inside c_inner)
    m_half_width: float = 11.0
    m_height: float = 18.0
    m_stroke: float = 4.2
    m_valley_depth: float = 9.0  # how far the middle V drops from the top


@dataclass(frozen=True)
class SunGearParams:
    """Sun/gear rays around the CM circle. Origin = shared center."""

    cx: float = 0.0
    cy: float = 0.0
    ray_count: int = 8
    # Core = CM disc; rays sit on the white disc edge (no yellow halo ring)
    core_radius: float = 30.0
    ray_inner: float = 30.0
    ray_outer: float = 72.0
    # Base width of each triangular ray at the disc (degrees of arc)
    ray_base_deg: float = 36.0
    rotation_deg: float = -90.0  # first ray points up
    # Drop E/W rays so "ISAR" / "Punk" can sit in the horizontal gaps
    skip_horizontal: bool = True


def ray_mid_angle(params: SunGearParams, index: int) -> float:
    return params.rotation_deg + index * (360.0 / params.ray_count)


def is_horizontal_ray(angle_deg: float, tol_deg: float = 1.0) -> bool:
    """True for rays aimed left or right (≈ 0° or 180°)."""
    a = angle_deg % 360.0
    return min(abs(a - 0.0), abs(a - 180.0), abs(a - 360.0)) <= tol_deg


@dataclass(frozen=True)
class IsarCurveParams:
    """Shallow river arc under the mark (Munich / Isar wink)."""

    y: float = 86.0
    half_width: float = 70.0
    sag: float = 14.0
    stroke_width: float = 5.0


def polar(cx: float, cy: float, radius: float, angle_deg: float) -> Point:
    rad = math.radians(angle_deg)
    return (cx + radius * math.cos(rad), cy + radius * math.sin(rad))


def ray_triangle(
    params: SunGearParams,
    index: int,
) -> list[Point]:
    """Isosceles triangle ray: base on the ring, tip pointing outward (sun spike)."""
    mid = ray_mid_angle(params, index)
    half = params.ray_base_deg / 2.0
    return [
        polar(params.cx, params.cy, params.ray_inner, mid - half),
        polar(params.cx, params.cy, params.ray_outer, mid),  # tip
        polar(params.cx, params.cy, params.ray_inner, mid + half),
    ]


def all_rays(params: SunGearParams) -> list[list[Point]]:
    rays: list[list[Point]] = []
    for i in range(params.ray_count):
        if params.skip_horizontal and is_horizontal_ray(ray_mid_angle(params, i)):
            continue
        rays.append(ray_triangle(params, i))
    return rays


def isar_quadratic_path(params: IsarCurveParams, cx: float) -> str:
    """
    Single quadratic Bézier: left → bottom → right.
    Control point sits below the chord so the curve 'flows' under the mark.
    """
    x0, y0 = cx - params.half_width, params.y
    x1, y1 = cx + params.half_width, params.y
    cpx, cpy = cx, params.y + params.sag
    return f"M {fmt(x0)} {fmt(y0)} Q {fmt(cpx)} {fmt(cpy)} {fmt(x1)} {fmt(y1)}"


def fmt(n: float) -> str:
    # Compact but stable SVG numbers
    s = f"{n:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"


def points_to_svg(points: Sequence[Point]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def bbox_of(points: Iterable[Point]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for x, y in points:
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def mark_extent(
    gear: SunGearParams,
    river: IsarCurveParams | None,
    *,
    include_split_wordmark: bool = False,
    word_font_size: float = 36.0,
) -> tuple[float, float, float, float]:
    pts: list[Point] = []
    for ray in all_rays(gear):
        pts.extend(ray)
    for a in range(0, 360, 15):
        pts.append(polar(gear.cx, gear.cy, gear.core_radius, a))
    # Vertical rays still reach ray_outer
    pts.append((gear.cx, gear.cy - gear.ray_outer))
    pts.append((gear.cx, gear.cy + gear.ray_outer))
    if river:
        pts.append((gear.cx - river.half_width, river.y))
        pts.append((gear.cx + river.half_width, river.y))
        pts.append((gear.cx, river.y + river.sag + river.stroke_width))
    if include_split_wordmark:
        # Approximate text boxes in the cleared E/W ray slots
        gap = 10.0
        left_w = word_font_size * 0.72 * 4 + word_font_size * 0.06 * 3  # ISAR
        right_w = word_font_size * 0.72 * 4 + word_font_size * 0.06 * 3  # Punk
        x_left = gear.cx - gear.core_radius - gap
        x_right = gear.cx + gear.core_radius + gap
        pts.append((x_left - left_w, gear.cy - word_font_size * 0.4))
        pts.append((x_left, gear.cy + word_font_size * 0.4))
        pts.append((x_right, gear.cy - word_font_size * 0.4))
        pts.append((x_right + right_w, gear.cy + word_font_size * 0.4))
    return bbox_of(pts)


def svg_circle(cx: float, cy: float, r: float, fill: str, **attrs: str) -> str:
    extra = "".join(f' {k}="{v}"' for k, v in attrs.items())
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{fill}"{extra}/>'


def svg_ring(
    cx: float,
    cy: float,
    r_outer: float,
    r_inner: float,
    fill: str,
) -> str:
    """Annulus via even-odd path."""
    # Outer circle (CW) + inner circle (CCW) for evenodd hole
    d = (
        f"M {fmt(cx + r_outer)} {fmt(cy)} "
        f"A {fmt(r_outer)} {fmt(r_outer)} 0 1 1 {fmt(cx - r_outer)} {fmt(cy)} "
        f"A {fmt(r_outer)} {fmt(r_outer)} 0 1 1 {fmt(cx + r_outer)} {fmt(cy)} Z "
        f"M {fmt(cx + r_inner)} {fmt(cy)} "
        f"A {fmt(r_inner)} {fmt(r_inner)} 0 1 0 {fmt(cx - r_inner)} {fmt(cy)} "
        f"A {fmt(r_inner)} {fmt(r_inner)} 0 1 0 {fmt(cx + r_inner)} {fmt(cy)} Z"
    )
    return f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/>'


def svg_polygon(points: Sequence[Point], fill: str) -> str:
    return f'<polygon points="{points_to_svg(points)}" fill="{fill}"/>'


def open_ring_path(
    cx: float,
    cy: float,
    r_outer: float,
    r_inner: float,
    gap_deg: float,
    gap_center_deg: float = 0.0,
) -> str:
    """
    Annulus with a wedge removed (the C).
    Arc runs the long way from gap+ to gap- (sweep ≈ 360 - gap).
    SVG angles: 0° = east, positive CCW — we use the same via polar().
    """
    half = gap_deg / 2.0
    a0 = gap_center_deg + half  # start after gap (going CCW around the long arc)
    a1 = gap_center_deg - half + 360.0  # end before gap

    # For large-arc flag: sweep of (360 - gap) > 180 → large-arc = 1
    large = 1 if (360.0 - gap_deg) > 180.0 else 0

    o0 = polar(cx, cy, r_outer, a0)
    o1 = polar(cx, cy, r_outer, a1)
    i1 = polar(cx, cy, r_inner, a1)
    i0 = polar(cx, cy, r_inner, a0)

    # Outer arc a0 → a1 (CCW), line to inner, inner arc a1 → a0 (CW), close
    return (
        f"M {fmt(o0[0])} {fmt(o0[1])} "
        f"A {fmt(r_outer)} {fmt(r_outer)} 0 {large} 1 {fmt(o1[0])} {fmt(o1[1])} "
        f"L {fmt(i1[0])} {fmt(i1[1])} "
        f"A {fmt(r_inner)} {fmt(r_inner)} 0 {large} 0 {fmt(i0[0])} {fmt(i0[1])} Z"
    )


def m_letter_path(cx: float, cy: float, cm: CMParams) -> str:
    """
    Geometric capital M as a single filled outline (constant stroke feel).
    Built from outer silhouette: left stem, left peak, valley, right peak, right stem.
    """
    w = cm.m_half_width
    h = cm.m_height
    t = cm.m_stroke
    v = cm.m_valley_depth
    # Vertical center the glyph on cy
    top = cy - h / 2.0
    bot = cy + h / 2.0
    mid_y = top + v

    # Outer path clockwise starting bottom-left
    # Stems are width t; apexes are sharp; valley has a flat-ish notch of width ~t
    left = cx - w
    right = cx + w
    # Inner edges of stems
    left_i = left + t
    right_i = right - t
    # Valley notch half-width
    vh = t * 0.45

    pts = [
        (left, bot),
        (left, top),
        (left_i, top),
        (cx - vh, mid_y),  # down into valley from left peak inner
        (cx + vh, mid_y),
        (right_i, top),
        (right, top),
        (right, bot),
        (right_i, bot),
        (right_i, top + t * 1.15),  # inner right stem up
        (cx + vh * 0.35, mid_y + t * 0.85),  # valley floor right
        (cx - vh * 0.35, mid_y + t * 0.85),  # valley floor left
        (left_i, top + t * 1.15),
        (left_i, bot),
    ]
    return "M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x, y in pts) + " Z"


def build_cm_circle(
    cx: float,
    cy: float,
    cm: CMParams,
    *,
    disc_fill: str = WHITE,
    ink: str = INK,
) -> str:
    """Electronics Circle CM badge — the star/sun core."""
    parts = [
        f'<g id="cm-circle">',
        svg_circle(cx, cy, cm.disc_radius, disc_fill),
        f'<path id="cm-c" fill="{ink}" d="{open_ring_path(cx, cy, cm.c_outer, cm.c_inner, cm.gap_deg)}"/>',
        svg_circle(cx + (cm.c_outer + cm.c_inner) / 2.0, cy, cm.dot_radius, ink),
        f'<path id="cm-m" fill="{ink}" d="{m_letter_path(cx, cy, cm)}"/>',
        "</g>",
    ]
    return "\n  ".join(parts)


def build_mark_group(
    gear: SunGearParams,
    river: IsarCurveParams | None,
    *,
    ray_fill: str = SUN,
    river_stroke: str = CYAN,
    cm: CMParams | None = None,
) -> str:
    cm = cm or CMParams(disc_radius=gear.core_radius)
    parts: list[str] = ['<g id="isarpunk-mark">']

    # Rays first so CM white disc paints over bases for a clean sit-on-disc join
    for ray in all_rays(gear):
        parts.append(svg_polygon(ray, ray_fill))

    # CM circle is the center — no yellow halo ring
    parts.append(build_cm_circle(gear.cx, gear.cy, cm))

    if river:
        d = isar_quadratic_path(river, gear.cx)
        parts.append(
            f'<path id="isar-curve" d="{d}" fill="none" '
            f'stroke="{river_stroke}" stroke-width="{fmt(river.stroke_width)}" '
            f'stroke-linecap="round"/>'
        )

    parts.append("</g>")
    return "\n  ".join(parts)


def build_wordmark(
    x: float,
    y: float,
    *,
    text: str = "ISARPUNK",
    fill: str = INK,
    font_size: float = 42.0,
    anchor: str = "start",
    element_id: str = "wordmark",
) -> str:
    # Geometric sans stack; system fonts OK for SVG-in-browser / Inkscape
    return (
        f'<text id="{element_id}" x="{fmt(x)}" y="{fmt(y)}" '
        f'fill="{fill}" font-size="{fmt(font_size)}" font-weight="700" '
        f'font-family="Montserrat, Arial Narrow, Arial, Helvetica, sans-serif" '
        f'letter-spacing="0.08em" text-anchor="{anchor}" '
        f'dominant-baseline="middle">{text}</text>'
    )


def build_split_name(
    gear: SunGearParams,
    *,
    fill: str = WHITE,
    font_size: float = 15.0,
    gap: float = 8.0,
) -> str:
    """ISAR left of the sun, Punk right — sits in the cleared horizontal ray slots."""
    y = gear.cy
    x_left = gear.cx - gear.core_radius - gap
    x_right = gear.cx + gear.core_radius + gap
    return "\n  ".join(
        [
            build_wordmark(
                x_left,
                y,
                text="ISAR",
                fill=fill,
                font_size=font_size,
                anchor="end",
                element_id="name-isar",
            ),
            build_wordmark(
                x_right,
                y,
                text="Punk",
                fill=fill,
                font_size=font_size,
                anchor="start",
                element_id="name-punk",
            ),
        ]
    )


def build_tagline(
    x: float,
    y: float,
    *,
    text: str = "Hack your life / Save Oma",
    fill: str = PURPLE,
    font_size: float = 14.0,
    anchor: str = "start",
) -> str:
    return (
        f'<text id="tagline" x="{fmt(x)}" y="{fmt(y)}" '
        f'fill="{fill}" font-size="{fmt(font_size)}" font-weight="500" '
        f'font-family="Montserrat, Arial, Helvetica, sans-serif" '
        f'letter-spacing="0.04em" text-anchor="{anchor}">{text}</text>'
    )


def render_svg(
    *,
    mode: str,
    include_river: bool,
    include_tagline: bool,
    padding: float = 16.0,
) -> str:
    gear = SunGearParams()
    river = IsarCurveParams() if include_river else None
    name_size = 15.0

    if mode == "icon":
        min_x, min_y, max_x, max_y = mark_extent(
            gear, river, include_split_wordmark=True, word_font_size=name_size
        )
        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        tx, ty = -min_x + padding, -min_y + padding
        body = "\n  ".join(
            [
                build_mark_group(gear, river),
                build_split_name(gear, fill=WHITE, font_size=name_size),
            ]
        )
        content = f'<g transform="translate({fmt(tx)} {fmt(ty)})">\n  {body}\n</g>'
        vb = f"0 0 {fmt(width)} {fmt(height)}"

    elif mode == "lockup":
        # Same split name as icon; optional tagline centered under the sun
        min_x, min_y, max_x, max_y = mark_extent(
            gear, river, include_split_wordmark=True, word_font_size=name_size
        )
        parts = [
            build_mark_group(gear, river),
            build_split_name(gear, fill=WHITE, font_size=name_size),
        ]
        if include_tagline:
            tag_y = max_y + 22.0
            parts.append(build_tagline(gear.cx, tag_y, fill=WHITE, anchor="middle"))
            max_y = tag_y + 8.0

        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        tx, ty = -min_x + padding, -min_y + padding
        body = "\n  ".join(parts)
        content = f'<g transform="translate({fmt(tx)} {fmt(ty)})">\n  {body}\n</g>'
        vb = f"0 0 {fmt(width)} {fmt(height)}"

    elif mode == "header":
        # 1600×400 Google Forms header — split name flanking scaled sun
        width, height = 1600.0, 400.0
        scale = 2.0
        mark_cx = 800.0
        mark_cy = 175.0
        local_gear = SunGearParams()
        local_river = IsarCurveParams() if include_river else None
        # Place split words in screen space around the scaled mark
        disc_screen = local_gear.core_radius * scale
        gap = 12.0
        font_size = 15.0 * scale  # same 15 in mark-space, readable on banner
        parts = [
            f'<rect width="{fmt(width)}" height="{fmt(height)}" fill="{PURPLE}"/>',
            f'<rect y="{fmt(height - 12)}" width="{fmt(width)}" height="12" fill="{YELLOW}"/>',
            f'<g transform="translate({fmt(mark_cx)} {fmt(mark_cy)}) scale({fmt(scale)})">\n  '
            f"{build_mark_group(local_gear, local_river)}\n</g>",
            build_wordmark(
                mark_cx - disc_screen - gap,
                mark_cy,
                text="ISAR",
                fill=WHITE,
                font_size=font_size,
                anchor="end",
                element_id="name-isar",
            ),
            build_wordmark(
                mark_cx + disc_screen + gap,
                mark_cy,
                text="Punk",
                fill=WHITE,
                font_size=font_size,
                anchor="start",
                element_id="name-punk",
            ),
        ]
        if include_tagline:
            parts.append(
                build_tagline(
                    mark_cx,
                    mark_cy + disc_screen + 70.0,
                    fill=YELLOW,
                    font_size=20.0,
                    anchor="middle",
                )
            )
        content = "\n  ".join(parts)
        vb = f"0 0 {fmt(width)} {fmt(height)}"

    else:
        raise ValueError(f"Unknown mode: {mode}")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="IsarPunk">
  <title>IsarPunk</title>
  {content}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate IsarPunk logo SVG from computed geometry.")
    parser.add_argument(
        "--mode",
        choices=("icon", "lockup", "header"),
        default="lockup",
        help="icon = mark only; lockup = mark + wordmark; header = 1600×400 form banner",
    )
    parser.add_argument("--no-river", action="store_true", help="Omit Isar curve under the mark")
    parser.add_argument("--tagline", action="store_true", help="Include tagline text")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output SVG path (default: Brand/logo/isarpunk-<mode>.svg)",
    )
    args = parser.parse_args()

    out = args.output
    if out is None:
        out = Path(__file__).resolve().parent.parent / "logo" / f"isarpunk-{args.mode}.svg"

    out.parent.mkdir(parents=True, exist_ok=True)
    svg = render_svg(
        mode=args.mode,
        include_river=not args.no_river,
        include_tagline=args.tagline,
    )
    out.write_text(svg, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
