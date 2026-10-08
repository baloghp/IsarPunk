#!/usr/bin/env python3
"""
IsarPunk print builder — renders workshop artifacts as print-ready A4 PDFs.

  python3 Print/build_print.py               # build everything
  python3 Print/build_print.py layer-sort    # build one artifact
  python3 Print/build_print.py --refresh     # re-download logos

Pipeline: stdlib composes an SVG page (mm units) -> Inkscape exports PDF.
Logos are downloaded once into Print/assets/logos/ so later builds work offline.
QR codes need `segno` (pip install --user segno); they point to the GitHub Pages
link page (docs/index.html), which this script also generates.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "logos"
BUILD = ROOT / "build"
OUT = ROOT / "out"
BRAND_MARK = ROOT.parent / "Brand" / "logo" / "isarpunk.svg"
CM_MARK = ROOT.parent / "Brand" / "logo" / "CM_icon.svg"
DOCS = ROOT.parent / "docs"
PAGES_URL = "https://baloghp.github.io/IsarPunk/"

# QR topics -> section on the GitHub Pages link page. Cards reference the key.
# Links: (kind, DE label, EN label, url, note)
QR_TOPICS = {
    "iso": {
        "cards": "C7",
        "title": ("Linux Mint herunterladen", "Download Linux Mint"),
        "intro": ("Nimm die Cinnamon Edition — du lädst eine .iso-Datei herunter.",
                  "Take the Cinnamon Edition — you download an .iso file."),
        "links": [
            ("web", "Offizielle Download-Seite", "official download page", "https://www.linuxmint.com/download.php", ""),
            ("video", "Linux Mint – ganz leicht installiert", "", "https://youtu.be/isZ8ng5dr9c", "heise & c't · 8:23"),
            ("video", "Linux Mint installieren in 5 Minuten", "", "https://youtu.be/5QtWkLWRjis", "ELIX · 6:09"),
        ],
    },
    "stick": {
        "cards": "C8 · D7",
        "title": ("Live-Stick erstellen", "Make a live USB stick"),
        "intro": ("Achtung: Das löscht alles auf dem USB-Stick. Nur einen leeren Stick verwenden — und nur mit Erlaubnis.",
                  "Warning: this erases the USB stick. Use an empty stick — and only with permission."),
        "links": [
            ("video", "Linux Mint USB-Stick erstellen – der Umstieg von Windows", "", "https://youtu.be/AkpEI2Y5Wgk", "Tuhl Teim DE · 16:02"),
            ("video", "Ein USB-Stick = alle Betriebssysteme? (Ventoy)", "", "https://youtu.be/duoTuzZo5Pc", "Alexander Metzger · 5:55"),
            ("video", "Bootfähiger USB-Stick mit balenaEtcher", "", "https://youtu.be/PHnGeNPWcLE", "euroNAS · 1:19"),
        ],
    },
    "boot": {
        "cards": "C9 · D5",
        "title": ("Boot-Menü-Taste finden", "Find the boot-menu key"),
        "intro": ("Direkt nach dem Einschalten mehrmals die Taste drücken. Häufig: Acer F12 · Asus Esc · Dell F12 · "
                  "HP Esc, dann F9 · Lenovo F12 · Toshiba F12 · Samsung Esc · Apple: Option-Taste halten.",
                  "Press the key repeatedly right after switching on."),
        "links": [
            ("web", "Tabelle aller Hersteller", "table of all manufacturers", "https://www.disk-image.com/faq-bootmenu.htm", "Englisch"),
            ("video", "Boot-Menü aus Windows heraus öffnen", "", "https://youtu.be/K1z7BCGaRKA", "IT Tweak · 1:43"),
        ],
    },
    "lernen": {
        "cards": "C12 · D4",
        "title": ("Linux lernen", "Learn Linux"),
        "intro": ("Kurze Videos für den Einstieg.", "Short videos to get started."),
        "links": [
            ("video", "Win-10-Ende: So einfach geht's zu Linux!", "", "https://youtu.be/-H8T8CNsJQk", "c't 3003 · 14:58"),
            ("video", "Linux Mint ist 2026 einfacher als Windows", "", "https://youtu.be/4-MWA4JKQgc", "Frumpel Labs · 8:25"),
            ("video", "Grundlagen des Terminals in Linux", "", "https://youtu.be/Lme-KZQICFA", "Fmutix · 8:56"),
        ],
    },
    "projekte": {
        "cards": "D19",
        "title": ("Projekte mit alten Geräten", "Projects with old devices"),
        "intro": ("Nur mit einer erwachsenen Person und nach den Regeln eurer Schule.",
                  "Only with an adult and following your school's rules."),
        "links": [
            ("section", "Entertainment-Projekte", "entertainment", "#unterhaltung", "Batocera · Jellyfin · Navidrome · OBS"),
            ("section", "Sicherheit & Privatsphäre", "security & privacy", "#privatsphaere", "Pi-hole · Nextcloud · Vaultwarden"),
            ("section", "Eigener Chat-Server", "own chat server", "#chat", "Matrix / Synapse"),
        ],
    },
    "unterhaltung": {
        "cards": "D16",
        "title": ("Entertainment-Projekte", "Entertainment projects"),
        "intro": ("Retro-Spiele, eigener Film- und Musikserver, Streamen.",
                  "Retro games, your own film and music server, streaming."),
        "links": [
            ("video", "Batocera: Spielkonsole auf einem USB-Stick", "", "https://youtu.be/1EVAKRC0mUY", "c't 3003 · 12:00"),
            ("video", "Jellyfin: Das eigene Netflix, nur kostenlos", "", "https://youtu.be/wbslt7r2-Xk", "c't 3003 · 14:37"),
            ("video", "Navidrome: Eigene Musik streamen ohne Abo", "", "https://youtu.be/gb4hzQUVA1M", "knowaTEL · 12:25"),
            ("video", "OBS Studio Grundlagen", "", "https://youtu.be/9hfdHhMXkxo", "Nilson1489 · 12:03"),
        ],
    },
    "privatsphaere": {
        "cards": "D17",
        "title": ("Sicherheit & Privatsphäre", "Security & privacy"),
        "intro": ("Werbung blockieren, eigene Cloud, eigener Passwort-Manager.",
                  "Block ads, your own cloud, your own password manager."),
        "links": [
            ("video", "Pi-hole: Werbung im ganzen Netz blockieren", "", "https://youtu.be/oF1_ggDZaOM", "Niels Maseberg · 15:08"),
            ("video", "Nextcloud All-in-One installieren", "", "https://youtu.be/h5l2y00yeOY", "IT-ION · 16:33"),
            ("video", "Vaultwarden: Passwort-Manager selbst hosten", "", "https://youtu.be/Ej-Y5yZOHzQ", "TechWissen DE · 7:18"),
        ],
    },
    "chat": {
        "cards": "D18",
        "title": ("Eigener Chat-Server", "Own chat server"),
        "intro": ("Nur mit Erwachsenen und nach den Regeln eurer Schule.",
                  "Only with adults and following your school's rules."),
        "links": [
            ("video", "Matrix: sichere Kommunikation mit Open Source", "", "https://youtu.be/INkN_HvrxHI", "Linux-Hanny · 9:35"),
            ("video", "Synapse-Matrix-Server installieren", "", "https://youtu.be/2G0ewKSozs0", "The Morpheus Tutorials · 19:12"),
        ],
    },
    "hilfe": {
        "cards": "",
        "title": ("Hilfe in München", "Help in Munich"),
        "intro": ("Repair-Shops, Repair-Cafés und mehr auf der Karte von Circular Munich.",
                  "Repair shops, repair cafés and more on Circular Munich's map."),
        "links": [
            ("web", "CircularCity Map", "", "https://circular-munich.com/circularcitymap/", ""),
        ],
    },
}


def qr_url(topic: str) -> str:
    return f"{PAGES_URL}#{topic}"

TEAL = "#005577"
SUN = "#F5D400"
INK = "#1D2B36"
CUT = "#8A9BA8"
EN_GREY = "#5F7280"
EN_SCALE = 0.72  # English runs at this fraction of the German size
FONT = "'Open Sans', 'Noto Sans', sans-serif"
MONO = "'Noto Sans Mono', 'Liberation Mono', monospace"
RIVER = "#5EC8E8"

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

SI = "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{}.svg"
LUCIDE = "https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{}.svg"
COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/{}"

# key -> download URL. Simple Icons: CC0 · Lucide: ISC · Commons: see file page.
LOGO_SOURCES = {
    "laptop": LUCIDE.format("laptop"),
    "smartphone": LUCIDE.format("smartphone"),
    "tablet": LUCIDE.format("tablet"),
    "gamepad": LUCIDE.format("gamepad-2"),
    "windows": SI.format("windows"),
    "android": SI.format("android"),
    "ios": SI.format("ios"),
    "macos": SI.format("macos"),
    "tux": COMMONS.format("Tux.svg"),
    "roblox": SI.format("roblox"),
    "discord": SI.format("discord"),
    "spotify": SI.format("spotify"),
    "youtube": SI.format("youtube"),
    "capcut": COMMONS.format("CapCut_logo.svg"),
    "snapchat": SI.format("snapchat"),
    "instagram": SI.format("instagram"),
    "tiktok": SI.format("tiktok"),
    "fortnite": SI.format("fortnite"),
    "minecraft": SI.format("minecraft"),
    "chrome": COMMONS.format("Google_Chrome_icon_(February_2022).svg"),
    "steam": SI.format("steam"),
    "word": SI.format("microsoftword"),
}

LOGO_CREDITS_DE = ("Logos sind Marken ihrer Inhaber und dienen nur der Identifikation.",
                   "Logos are trademarks of their owners, used for identification only.")
ICON_CREDITS = ("Icons: Simple Icons (CC0), Lucide (ISC), Wikimedia Commons · "
                "Tux: Larry Ewing (lewing@isc.tamu.edu) & The GIMP")


# ---------------------------------------------------------------- assets

def fetch_logos(refresh: bool = False) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for key, url in LOGO_SOURCES.items():
        target = ASSETS / f"{key}.svg"
        if target.exists() and not refresh:
            continue
        print(f"  fetch {key:<11} {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "IsarPunkPrint/1.0 (workshop print materials)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            target.write_bytes(resp.read())


def _local(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        ns, name = tag[1:].split("}", 1)
        return ns, name
    return SVG_NS, tag


def embed_svg(path: Path, prefix: str, x: float, y: float, w: float, h: float,
              color: str | None = None, extra: str = "", view_box: str | None = None) -> str:
    """Return a nested <svg> placing `path` into the box, ids namespaced by prefix."""
    root = ET.parse(path).getroot()
    view_box = view_box or root.get("viewBox") or f"0 0 {root.get('width')} {root.get('height')}"

    def clean(el: ET.Element) -> None:
        for child in list(el):
            ns, name = _local(child.tag) if isinstance(child.tag, str) else ("", "")
            if ns != SVG_NS or name in ("metadata", "title", "desc"):
                el.remove(child)
            else:
                clean(child)
        for attr in list(el.attrib):
            ns, _ = _local(attr)
            if ns not in (SVG_NS, XLINK_NS) and attr.startswith("{"):
                del el.attrib[attr]
            elif attr == "id":
                el.set("id", f"{prefix}-{el.get('id')}")
        for attr, val in el.attrib.items():
            if "#" in val:
                val = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}-\1)", val)
                if attr in ("href", f"{{{XLINK_NS}}}href") and val.startswith("#"):
                    val = f"#{prefix}-{val[1:]}"
                el.set(attr, val)

    clean(root)

    # Root presentation attributes (fill/stroke on Lucide & Simple Icons) move onto a wrapper group.
    style = {k: v for k, v in root.attrib.items()
             if k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin")}
    if color:
        style = {k: (color if v == "currentColor" else v) for k, v in style.items()}
        if "stroke" not in style:
            style["fill"] = color
    group_attrs = " ".join(f'{k}="{v}"' for k, v in style.items())
    inner = "".join(ET.tostring(c, encoding="unicode") for c in root)
    inner = re.sub(r'\sxmlns(:\w+)?="[^"]+"', "", inner)
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'viewBox="{view_box}" preserveAspectRatio="xMidYMid meet" overflow="visible">'
            f'<g {group_attrs} {extra}>{inner}</g></svg>')


# ---------------------------------------------------------------- page

class Page:
    """A4 portrait SVG page in millimetres."""

    W, H = 210.0, 297.0

    def __init__(self, landscape: bool = False) -> None:
        if landscape:
            self.W, self.H = Page.H, Page.W
        self.defs: list[str] = []
        self.body: list[str] = []

    def add(self, markup: str) -> None:
        self.body.append(markup)

    def text(self, x: float, y: float, s: str, size_pt: float, *, weight: int = 400,
             fill: str = INK, anchor: str = "start", spacing: float = 0,
             en: str = "", en_fill: str = EN_GREY) -> None:
        """German text; `en` follows inline in brackets, smaller and lighter."""
        size = size_pt * 0.3528

        def esc(t: str) -> str:
            t = t.replace("&", "&amp;").replace("<", "&lt;")
            return re.sub(r"`([^`]+)`", rf'<tspan font-family="{MONO}" font-weight="700" fill="{TEAL}">\1</tspan>', t)

        s = esc(s)
        if en:
            s += (f' <tspan font-size="{size * EN_SCALE:.3f}" font-weight="400" fill="{en_fill}" '
                  f'letter-spacing="0">({esc(en)})</tspan>')
        self.add(f'<text xml:space="preserve" x="{x:.3f}" y="{y:.3f}" font-family="{FONT}" font-size="{size:.3f}" '
                 f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
                 f'letter-spacing="{spacing}">{s}</text>')

    def svg(self) -> str:
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="{SVG_NS}" xmlns:xlink="{XLINK_NS}" width="{self.W}mm" height="{self.H}mm" '
                f'viewBox="0 0 {self.W} {self.H}"><defs>{"".join(self.defs)}</defs>'
                f'<rect width="{self.W}" height="{self.H}" fill="#fff"/>{"".join(self.body)}</svg>')


def wrap(s: str, width_mm: float, size_pt: float, bold: bool = False) -> list[str]:
    """Greedy word wrap using an average Open Sans glyph width."""
    per_char = size_pt * 0.3528 * (0.58 if bold else 0.53)
    limit = max(1, int(width_mm / per_char))
    lines: list[str] = []
    for word in re.findall(r"`[^`]+`\S*|\S+", s):
        if lines and len(lines[-1].replace("`", "")) + 1 + len(word.replace("`", "")) <= limit:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def export_pdf(pages: list[Page], name: str) -> Path:
    inkscape = shutil.which("inkscape")
    if not inkscape:
        sys.exit("Inkscape is required (sudo dnf install inkscape).")
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    pdfs = []
    for i, page in enumerate(pages, 1):
        svg_path = BUILD / f"{name}-{i}.svg"
        svg_path.write_text(page.svg(), encoding="utf-8")
        pdf_path = BUILD / f"{name}-{i}.pdf"
        subprocess.run([inkscape, str(svg_path), "--export-type=pdf",
                        f"--export-filename={pdf_path}"], check=True, capture_output=True)
        pdfs.append(pdf_path)
    target = OUT / f"{name}.pdf"
    if len(pdfs) == 1:
        shutil.copy(pdfs[0], target)
    else:
        merge = shutil.which("qpdf") or shutil.which("pdfunite")
        if not merge:
            sys.exit("Multi-page artifacts need qpdf or pdfunite (poppler-utils).")
        args = ([merge, "--empty", "--pages", *map(str, pdfs), "--", str(target)]
                if merge.endswith("qpdf") else [merge, *map(str, pdfs), str(target)])
        subprocess.run(args, check=True)
    return target


def page_header(page: Page, title: tuple[str, str], subtitle: tuple[str, str]) -> None:
    page.add(embed_svg(BRAND_MARK, "brand", 9, 5.5, 25, 19))
    page.text(37, 13, title[0], 15, weight=800, fill=TEAL, en=title[1])
    page.text(37, 18.5, subtitle[0], 8)
    page.text(37, 22.3, f"({subtitle[1]})", 8 * EN_SCALE, fill=EN_GREY)
    page.add(embed_svg(CM_MARK, "cm", page.W - 10 - 13, 8.5, 13, 13))
    page.text(page.W - 25.5, 13.8, "Circular", 7.5, weight=700, anchor="end")
    page.text(page.W - 25.5, 17.6, "Munich e.V.", 7.5, weight=700, anchor="end")


NOT_FOR_DISTRIBUTION = ("Workshop-Material, nicht zur Weitergabe.", "workshop material, not for distribution")


def page_footer(page: Page, note: tuple[str, str] = NOT_FOR_DISTRIBUTION) -> None:
    fy = page.H - 9.5
    page.text(10, fy, f"© 2026 Circular Munich e.V. & Peter Balogh — alle Rechte vorbehalten. {note[0]}",
              5.6, fill=CUT, en=f"all rights reserved; {note[1]}", en_fill=CUT)
    page.text(10, fy + 3.1, LOGO_CREDITS_DE[0], 5.6, fill=CUT, en=LOGO_CREDITS_DE[1], en_fill=CUT)
    page.text(10, fy + 5.9, ICON_CREDITS, 4.2, fill=CUT)


# ---------------------------------------------------------------- layer sort (Set A)

@dataclass
class Card:
    id: str
    name: str
    logo: str
    tile: str | None = None    # tile background; None = logo stands on its own
    color: str | None = None   # recolour for monochrome icons
    wide: bool = False         # wordmark-style logo: give it the full card width
    view_box: str | None = None  # crop loose icon viewBoxes to the glyph
    extra: str = ""            # extra attributes for the logo group (e.g. transform)
    en: str = ""               # English name, only where it differs from the German


LAYER_ROWS: list[tuple[str, str, list[Card]]] = [
    ("GERÄT", "DEVICE", [
        Card("A1", "Laptop", "laptop", "#E6EEF3", INK),
        Card("A2", "Smartphone", "smartphone", "#E6EEF3", INK),
        Card("A3", "Tablet", "tablet", "#E6EEF3", INK, extra='transform="rotate(90 12 12)"'),
        Card("A4", "Spielekonsole", "gamepad", "#E6EEF3", INK, en="Game console"),
    ]),
    ("BETRIEBSSYSTEM", "OPERATING SYSTEM", [
        Card("A5", "Windows", "windows", "#0078D4", "#FFFFFF"),
        Card("A6", "Android", "android", "#3DDC84", "#073042"),
        Card("A7", "iOS", "ios", "#000000", "#FFFFFF"),
        Card("A8", "macOS", "macos", "#E8E8ED", "#1D1D1F"),
        Card("A9", "Linux", "tux"),
    ]),
    ("APP", "APP", [
        Card("A10", "Roblox", "roblox", "#000000", "#FFFFFF"),
        Card("A11", "Discord", "discord", "#5865F2", "#FFFFFF"),
        Card("A12", "Spotify", "spotify", "#121212", "#1ED760"),
        Card("A13", "YouTube", "youtube", "#FFFFFF", "#FF0000"),
        Card("A14", "CapCut", "capcut", wide=True),
        Card("A15", "Snapchat", "snapchat", "#FFFC00", "#000000"),
        Card("A16", "Instagram", "instagram", "url(#ig-grad)", "#FFFFFF"),
        Card("A17", "TikTok", "tiktok", "#000000", "#FFFFFF"),
        Card("A18", "Fortnite", "fortnite", "#2B1B5A", "#FFFFFF"),
        Card("A19", "Minecraft", "minecraft", color="#3C8527", wide=True, view_box="0 9.8 24 4.4"),
        Card("A20", "Chrome", "chrome"),
        Card("A21", "Steam", "steam", "#171A21", "#FFFFFF"),
        Card("A22", "Word", "word", "#185ABD", "#FFFFFF"),
    ]),
]

COLS = 5
CARD_W = 38.0
CARD_H = 42.0
TILE = 24.0
BAND_H = 11.0
SECTION_GAP = 4.0


def draw_card(page: Page, c: Card, x: float, y: float) -> None:
    page.add(f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" fill="#fff" '
             f'stroke="{CUT}" stroke-width="0.2"/>')
    page.text(x + 2, y + 4, c.id, 5, weight=600, fill=CUT)

    tx, ty = x + (CARD_W - TILE) / 2, y + 5.5
    logo = ASSETS / f"{c.logo}.svg"
    prefix = c.id.lower()
    if c.wide:
        page.add(embed_svg(logo, prefix, x + 3, ty, CARD_W - 6, TILE, c.color, c.extra, c.view_box))
    elif c.tile:
        border = ' stroke="#D5DDE3" stroke-width="0.3"' if c.tile.upper() == "#FFFFFF" else ""
        page.add(f'<rect x="{tx}" y="{ty}" width="{TILE}" height="{TILE}" rx="5.5" fill="{c.tile}"{border}/>')
        pad = 5.0
        if c.logo == "tiktok":
            # TikTok's chromatic offset: cyan and red ghosts behind the white glyph.
            for dx, col in ((-0.45, "#25F4EE"), (0.45, "#FE2C55")):
                page.add(embed_svg(logo, f"{prefix}{col[1:]}", tx + pad + dx, ty + pad + dx,
                                   TILE - 2 * pad, TILE - 2 * pad, col))
        page.add(embed_svg(logo, prefix, tx + pad, ty + pad, TILE - 2 * pad, TILE - 2 * pad,
                           c.color, c.extra, c.view_box))
    else:
        page.add(embed_svg(logo, prefix, tx - 1, ty - 1, TILE + 2, TILE + 2, c.color, c.extra, c.view_box))

    if c.en:
        page.text(x + CARD_W / 2, y + CARD_H - 7, c.name, 9.5, weight=700, anchor="middle")
        page.text(x + CARD_W / 2, y + CARD_H - 3, f"({c.en})", 9.5 * EN_SCALE, anchor="middle", fill=EN_GREY)
    else:
        page.text(x + CARD_W / 2, y + CARD_H - 5, c.name, 9.5, weight=700, anchor="middle")


# Hand-mixed so no row of the cut sheet hints at a layer.
UNSOLVED_ORDER = ["A10", "A5", "A2", "A17", "A9",
                  "A20", "A13", "A7", "A4", "A11",
                  "A6", "A1", "A21", "A15", "A8",
                  "A19", "A3", "A12", "A22", "A16",
                  "A14", "A18"]


def layer_page() -> Page:
    page = Page()
    page.defs.append(
        '<linearGradient id="ig-grad" x1="0" y1="1" x2="1" y2="0">'
        '<stop offset="0" stop-color="#FEDA75"/><stop offset="0.3" stop-color="#FA7E1E"/>'
        '<stop offset="0.55" stop-color="#D62976"/><stop offset="0.8" stop-color="#962FBF"/>'
        '<stop offset="1" stop-color="#4F5BD5"/></linearGradient>')
    return page


def draw_band(page: Page, label: str, en: str, x: float, y: float) -> None:
    w = COLS * CARD_W
    page.add(f'<rect x="{x}" y="{y}" width="{w}" height="{BAND_H}" fill="{TEAL}" stroke="{CUT}" stroke-width="0.2"/>')
    page.add(f'<rect x="{x}" y="{y + BAND_H - 1.2}" width="{w}" height="1.2" fill="{SUN}"/>')
    page.text(x + w / 2, y + 7.3, label, 15, weight=800, fill="#FFFFFF", anchor="middle", spacing=1.2,
              en=en if en != label else "", en_fill="#BFD9E4")


def layer_sort_unsolved() -> Page:
    page = layer_page()
    page_header(page, ("Ebenen sortieren — Schnittbogen", "Layer sort — cut sheet"),
                ("Set A · Karten an den grauen Linien ausschneiden · 1 Blatt = 1 Team-Set",
                 "Set A · cut the cards along the grey lines · 1 sheet = 1 team set"))
    x0 = (Page.W - COLS * CARD_W) / 2
    y = 27.0
    cards = {c.id: c for _, _, row in LAYER_ROWS for c in row}
    for i, card_id in enumerate(UNSOLVED_ORDER):
        row, col = divmod(i, COLS)
        draw_card(page, cards[card_id], x0 + col * CARD_W, y + row * CARD_H)
    page_footer(page)
    return page


def layer_sort_solved() -> Page:
    page = layer_page()
    page_header(page, ("Ebenen sortieren — Lösung", "Layer sort — solution"),
                ("Set A · Gerät / Betriebssystem / App · Referenz für die Moderation — nicht ausschneiden",
                 "Set A · device / operating system / app · facilitator reference — do not cut"))
    x0 = (Page.W - COLS * CARD_W) / 2
    y = 27.0
    for label, en, cards in LAYER_ROWS:
        draw_band(page, label, en, x0, y)
        y += BAND_H
        for i, card in enumerate(cards):
            row, col = divmod(i, COLS)
            draw_card(page, card, x0 + col * CARD_W, y + row * CARD_H)
        y += -(-len(cards) // COLS) * CARD_H + SECTION_GAP
    page_footer(page)
    return page


def layer_sort_board() -> Page:
    page = layer_page()
    page_header(page, ("Ebenen sortieren — Spielfeld", "Layer sort — board"),
                ("Set A · Karten auf die richtige Ebene legen · mehrfach drucken, nicht ausschneiden",
                 "Set A · place the cards on the right layer · print several, do not cut"))
    x0 = (Page.W - COLS * CARD_W) / 2
    y = 27.0
    for label, en, cards in LAYER_ROWS:
        draw_band(page, label, en, x0, y)
        y += BAND_H
        h = -(-len(cards) // COLS) * CARD_H
        page.add(f'<rect x="{x0}" y="{y}" width="{COLS * CARD_W}" height="{h}" fill="#F4F8FA" '
                 f'stroke="{CUT}" stroke-width="0.25" stroke-dasharray="1.5 1.2"/>')
        y += h + SECTION_GAP
    page_footer(page)
    return page


def build_layer_sort() -> Path:
    return export_pdf([layer_sort_board(), layer_sort_unsolved(), layer_sort_solved()], "A_Layer_Sort_Set_A")


# ---------------------------------------------------------------- station sheets (F1 / F2)

@dataclass
class Task:
    de: str
    en: str
    # ("line", de, en) -> labelled write-in line · ("choice", [(de, en), ...]) -> tick boxes
    answers: list[tuple] | None = None


F1_TASKS = [
    Task("Finde die Taste für das Boot-Menü, wähle den USB-Stick und starte das Live-System. Es wird nichts installiert.",
         "Find the boot-menu key, choose the USB stick and start the live system. Nothing is installed.",
         [("line", "Boot-Taste", "boot key")]),
    Task("Wie alt ist dieser Laptop und was steckt drin? Öffne das Terminal und tippe `hostnamectl`",
         "How old is this laptop and what is inside? Open Terminal and type `hostnamectl`",
         [("line", "Modell", "model"), ("line", "Firmware-Datum", "firmware date"),
          ("line", "Bonus `free -h`", "RAM")]),
    Task("Was ist anders zwischen den beiden Desktops? Nenne je eine Sache.",
         "What is different between the two desktops? Name one thing about each.",
         [("line", "Mint", ""), ("line", "Bazzite", "")]),
    Task("Finde die Spiele-Software auf Bazzite.",
         "Find the games software on Bazzite.",
         [("line", "Name", "")]),
    Task("Wird gerade etwas installiert?",
         "Is anything being installed right now?",
         [("choice", [("Ja", "yes"), ("Nein", "no")])]),
    Task("Was hat dieses Betriebssystem gekostet?",
         "What did this operating system cost?",
         [("line", "€", "")]),
]

F2_TASKS = [
    Task("Finde etwas zum Zocken – und ein Spiel, das startet.",
         "Find something to play games with – and one game that launches.",
         [("line", "App / Spiel", "app / game")]),
    Task("Finde etwas, um ein Referat zu schreiben.",
         "Find something to write a school report.", [("line", "App", "")]),
    Task("Finde etwas, um Videos zu schneiden.",
         "Find something to edit video.", [("line", "App", "")]),
    Task("Finde etwas zum Malen oder um Fotos zu bearbeiten.",
         "Find something to draw or edit photos.", [("line", "App", "")]),
    Task("Finde etwas, um Musik zu hören oder einen Film zu schauen.",
         "Find something to play music or watch a film.", [("line", "App", "")]),
    Task("Wie alt ist dieser Laptop, und was hat er neu gekostet?",
         "How old is this laptop, and what did it cost new?",
         [("line", "Jahr", "year"), ("line", "€ neu", "€ new")]),
    Task("Finde etwas, das du schon jeden Tag benutzt.",
         "Find something you already use every day.", [("line", "App", "")]),
    Task("Was kostet die ganze Software hier?",
         "What does all this software cost?", [("line", "€", "")]),
]

ANSWER_H = 8.0
ANSWER_COL = 44.0  # write-in lines start here, measured from the task text
TASK_PAD = 3.2


def task_height(t: Task, text_w: float) -> float:
    h = len(wrap(t.de, text_w, 10.5, bold=True)) * 4.6 + len(wrap(t.en, text_w, 10.5 * EN_SCALE)) * 3.5
    return h + len(t.answers or []) * ANSWER_H + 2 * TASK_PAD


def station_sheet(letter: str, code: str, title: tuple[str, str], goal: tuple[str, str],
                  tasks: list[Task], band: str, band_text: str) -> Page:
    page = Page()
    page_header(page, (f"Station {letter} — {title[0]}", title[1]),
                (f"{code} · {goal[0]}", f"{code} · {goal[1]}"))
    x0, w = 10.0, Page.W - 20
    y = 28.0

    page.add(f'<rect x="{x0}" y="{y}" width="{w}" height="14" rx="2.5" fill="{band}"/>')
    page.text(x0 + 5, y + 9.6, f"STATION {letter}", 17, weight=800, fill=band_text, spacing=1.5)
    y += 19

    text_x = x0 + 14
    text_w = w - 14 - 14
    for n, t in enumerate(tasks, 1):
        h = task_height(t, text_w)
        page.add(f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="#F4F8FA" '
                 f'stroke="#D5DDE3" stroke-width="0.3"/>')
        page.add(f'<circle cx="{x0 + 7}" cy="{y + 7.2}" r="4.2" fill="{SUN}"/>')
        page.text(x0 + 7, y + 8.9, str(n), 11, weight=800, anchor="middle")
        # self-check box: ticked when the task is done
        page.add(f'<rect x="{x0 + w - 10}" y="{y + 3.2}" width="6" height="6" rx="1" fill="#fff" '
                 f'stroke="{INK}" stroke-width="0.35"/>')

        ty = y + TASK_PAD + 3.6
        for line in wrap(t.de, text_w, 10.5, bold=True):
            page.text(text_x, ty, line, 10.5, weight=700)
            ty += 4.6
        ty -= 0.8
        for line in wrap(t.en, text_w, 10.5 * EN_SCALE):
            page.text(text_x, ty, line, 10.5 * EN_SCALE, fill=EN_GREY)
            ty += 3.5

        for ans in t.answers or []:
            ty += ANSWER_H
            base = ty - 1.6
            if ans[0] == "line":
                _, de, en = ans
                page.text(text_x, base, de, 8.5, weight=600, en=en)
                page.add(f'<line x1="{text_x + ANSWER_COL}" y1="{base + 0.6}" x2="{x0 + w - 14}" '
                         f'y2="{base + 0.6}" stroke="{CUT}" stroke-width="0.3"/>')
            else:
                cx = text_x
                for de, en in ans[1]:
                    page.add(f'<rect x="{cx}" y="{base - 3.6}" width="4.2" height="4.2" rx="0.8" fill="#fff" '
                             f'stroke="{INK}" stroke-width="0.35"/>')
                    page.text(cx + 6, base, de, 9, weight=600, en=en)
                    cx += 30
        y += h + 2.6

    page.text(x0 + w, y + 4, f"Geschafft:  ____ / {len(tasks)}", 10, weight=700, anchor="end",
              en="done", fill=TEAL)
    page_footer(page)
    return page


def build_stations() -> Path:
    a = station_sheet("A", "F1", ("Distro-Verkostung", "distro tasting"),
                      ("Ein ganzes Betriebssystem läuft vom USB-Stick – auf altem Laptop",
                       "a full operating system runs from a USB stick – on an old laptop"),
                      F1_TASKS, TEAL, "#FFFFFF")
    b = station_sheet("B", "F2", ("Schatzsuche", "treasure hunt"),
                      ("Spiele, Schul-Apps und Medien finden – und was kostet das alles?",
                       "find games, school apps and media – and what does it all cost?"),
                      F2_TASKS, RIVER, INK)
    return export_pdf([a, b], "F_Station_Sheets")


# ---------------------------------------------------------------- Measure In / Out cards

MEASURE_ROWS = [
    ("E1", "Ich könnte jemandem erklären, was ein Betriebssystem ist.",
     "I could explain what an operating system is."),
    ("E2", "Ich könnte Linux an einem Computer ausprobieren, ohne ihn kaputt zu machen.",
     "I could try Linux on a computer without breaking it."),
    ("E3", "Ich wüsste, was man mit einem alten Computer macht, den niemand mehr benutzt.",
     "I would know what to do with an old computer nobody uses."),
    ("B1", "Ein Laptop von 2015 ist eigentlich Elektroschrott.",
     "A laptop from 2015 is basically e-waste."),
    ("B2", "Auf Linux kann man nicht richtig zocken.",
     "You can't really game on Linux."),
    ("B3", "Ob ein Computer Sicherheitsupdates erhält, spielt eigentlich keine Rolle mehr.",
     "Whether a computer receives security updates does not really matter anymore."),
    ("B4", "Ein anderes Betriebssystem zu installieren macht den Computer kaputt.",
     "Installing a different OS breaks the computer."),
    ("B5", "Nur ein Profi kann einen alten Computer wieder brauchbar machen.",
     "Only a professional can make an old computer useful again."),
    ("B6", "Ältere Generationen können besser mit Technik umgehen als jüngere Generationen.",
     "Older generations are better at technology than younger generations."),
]

M_X0, M_W, M_H, M_Y0 = 10.0, 190.0, 64.0, 27.0
GREEN, RED = "#2F9E44", "#E03131"


def measure_question(page: Page, x: float, y: float, qid: str, de: str, en: str) -> None:
    confidence = qid.startswith("E")
    accent = TEAL if confidence else RIVER
    page.add(f'<rect x="{x}" y="{y}" width="{M_W}" height="{M_H}" fill="#fff" stroke="{CUT}" stroke-width="0.2"/>')
    page.add(f'<rect x="{x}" y="{y}" width="22" height="{M_H}" fill="{accent}"/>')
    page.text(x + 11, y + M_H / 2 + 3.5, qid, 24, weight=800, anchor="middle",
              fill="#FFFFFF" if confidence else INK)
    if qid == "B1":
        page.add(embed_svg(CM_MARK, "cm-b1", x + M_W - 17, y + 4, 13, 13))

    text_x, text_w = x + 28, M_W - 28 - (20 if qid == "B1" else 6)
    # largest size that keeps the German to three lines
    size = next(s for s in (22, 20, 18, 16) if len(wrap(de, text_w, s, bold=True)) <= 3)
    de_lines = wrap(de, text_w, size, bold=True)
    en_lines = wrap(f"({en})", text_w, size * EN_SCALE)
    lh, en_lh = size * 0.3528 * 1.25, size * EN_SCALE * 0.3528 * 1.3
    block = len(de_lines) * lh + 1.5 + len(en_lines) * en_lh
    ty = y + (M_H - block) / 2 + size * 0.3528 * 0.9
    for line in de_lines:
        page.text(text_x, ty, line, size, weight=700)
        ty += lh
    ty += 1.5
    for line in en_lines:
        page.text(text_x, ty, line, size * EN_SCALE, fill=EN_GREY)
        ty += en_lh


def measure_label(page: Page, x: float, y: float, de: str, en: str, kind: str) -> None:
    w = M_W / 2
    page.add(f'<rect x="{x}" y="{y}" width="{w}" height="{M_H}" fill="#fff" stroke="{CUT}" stroke-width="0.2"/>')
    cx, cy = x + w / 2, y + 22
    if kind == "yes":
        page.add(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{GREEN}"/>'
                 f'<polyline points="{cx - 5.5},{cy} {cx - 1.5},{cy + 4.5} {cx + 6},{cy - 4.5}" fill="none" '
                 f'stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    elif kind == "unsure":
        page.add(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{SUN}"/>')
        page.text(cx, cy + 5.4, "?", 30, weight=800, anchor="middle")
    elif kind == "no":
        page.add(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{RED}"/>'
                 f'<path d="M{cx - 4.5},{cy - 4.5} L{cx + 4.5},{cy + 4.5} M{cx + 4.5},{cy - 4.5} L{cx - 4.5},{cy + 4.5}" '
                 f'stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>')
    else:
        accent = TEAL if kind == "confidence" else RIVER
        page.add(f'<rect x="{x}" y="{y}" width="{w}" height="10" fill="{accent}"/>')
    ty = y + (45 if kind in ("yes", "unsure", "no") else 37)
    size = 22 if len(de) <= 12 else 17
    page.text(cx, ty, de, size, weight=800, anchor="middle", spacing=0.8)
    page.text(cx, ty + 9, f"({en})", 12, anchor="middle", fill=EN_GREY)


def build_measure() -> Path:
    slots: list = [("q", *row) for row in MEASURE_ROWS] + [
        [("STIMMT", "agree", "yes"), ("UNSICHER", "not sure", "unsure")],
        [("STIMMT NICHT", "disagree", "no"), ("SELBSTVERTRAUEN", "confidence", "confidence")],
        [("MEINUNGEN", "opinions", "opinions"), None],
    ]
    per_page = 4
    pages = []
    for start in range(0, len(slots), per_page):
        page = Page()
        n = start // per_page + 1
        page_header(page, ("Measure In / Out — Karten", "cards"),
                    (f"Fragen- und Spaltenkarten · ausschneiden, laminieren, wiederverwenden · Blatt {n}",
                     f"question and column cards · cut, laminate, reuse · sheet {n}"))
        for i, slot in enumerate(slots[start:start + per_page]):
            y = M_Y0 + i * M_H
            if isinstance(slot, tuple):
                measure_question(page, M_X0, y, *slot[1:])
            else:
                for j, label in enumerate(slot):
                    if label:
                        measure_label(page, M_X0 + j * M_W / 2, y, *label)
        page_footer(page)
        pages.append(page)
    return export_pdf(pages, "M_Measure_Cards")


# ---------------------------------------------------------------- mission cards (shared)

MC_W, MC_H = 135.0, 85.0      # landscape, 2 x 2 on landscape A4 with printer margins
MC_X0, MC_Y0 = (297.0 - 2 * 135.0) / 2, 26.0
MC_BAND = 12.0

TIERS = {  # tier -> (DE, EN, band colour, band text colour)
    "talk": ("Reden", "talk", RIVER, INK),
    "check": ("Prüfen", "check", "#7950F2", "#FFFFFF"),
    "safety": ("Sicherheit", "safety", RED, "#FFFFFF"),
    "do": ("Machen", "do", TEAL, "#FFFFFF"),
    "learn": ("Lernen", "learn", SUN, INK),
    "shop": ("Repair-Shop", "shop", GREEN, "#FFFFFF"),
    # Mission 2 paths
    "find": ("Finden", "find", RIVER, INK),
    "diagnose": ("Prüfen", "diagnose", "#7950F2", "#FFFFFF"),
    "revive": ("Wiederbeleben", "revive", TEAL, "#FFFFFF"),
    "family": ("Familie", "family", "#E8590C", "#FFFFFF"),
    "passon": ("Weitergeben", "pass on", "#E8590C", "#FFFFFF"),
    "recycle": ("Wertstoffhof", "recycle", "#868E96", "#FFFFFF"),
    "recover": ("Teile", "parts", "#495057", "#FFFFFF"),
    "project": ("Projekt", "project", "#D6336C", "#FFFFFF"),
}
JOKER_COLOURS = [RIVER, "#7950F2", RED, TEAL, SUN, GREEN]

SAFETY_RULES = (
    "1. Lösche nie einen Computer, der nicht dir gehört, ohne das OK der Besitzerin/des Besitzers. "
    "2. Vorher Backup. Wenn unsicher — in den Laden.",
    "1. Never wipe a computer that isn't yours without the owner's OK. "
    "2. Back up first. If unsure — take it to a shop.")

LIVE_USB_WARNING = (
    "Erstellen eines Live-Sticks löscht alle Daten auf dem USB-Stick. Nur einen leeren Stick verwenden "
    "oder vorher die Daten sichern. Nur mit Erlaubnis der Besitzerin/des Besitzers verwenden.",
    "Creating a live USB erases the contents of the USB stick. Use an empty stick or back up its "
    "contents first, and get the owner's permission.")


@dataclass
class MCard:
    id: str
    de: str
    en: str
    kind: str                 # tier key, "ending" or "start"
    qr: str | None = None     # QR_TOPICS key
    cm: bool = False          # inner-loop ending: shows the circularity icon
    note: tuple[str, str] | None = None   # boxed warning / safety text
    lot: str = ""             # Mission 2 reveal lot (A, B, C)
    sub: tuple[str, str] | None = None    # extra line under the text (e.g. project names)


def block_height(size: float, de_lines: list, en_lines: list) -> float:
    return len(de_lines) * size * 0.3528 * 1.28 + 1.2 + len(en_lines) * size * EN_SCALE * 0.3528 * 1.3


def fit_box(de: str, en: str, width: float, height: float, sizes: tuple) -> tuple[float, list, list]:
    """Largest size whose DE + EN block fits the box."""
    for s in sizes:
        de_lines, en_lines = wrap(de, width, s, bold=True), wrap(f"({en})", width, s * EN_SCALE)
        if block_height(s, de_lines, en_lines) <= height:
            break
    return s, de_lines, en_lines


def draw_text_block(page: Page, x: float, y: float, size: float, de_lines: list, en_lines: list,
                    fill: str = INK, en_fill: str = EN_GREY, anchor: str = "start") -> float:
    lh, en_lh = size * 0.3528 * 1.28, size * EN_SCALE * 0.3528 * 1.3
    ty = y + size * 0.3528
    for line in de_lines:
        page.text(x, ty, line, size, weight=700, fill=fill, anchor=anchor)
        ty += lh
    ty += 1.2
    for line in en_lines:
        page.text(x, ty, line, size * EN_SCALE, fill=en_fill, anchor=anchor)
        ty += en_lh
    return ty


def draw_note(page: Page, x: float, y: float, w: float, note: tuple[str, str]) -> float:
    """Boxed warning with a drawn triangle; returns the box height."""
    size = 6.3
    de_lines = wrap(note[0], w - 13, size, bold=True)
    en_lines = wrap(f"({note[1]})", w - 13, size * 0.9)
    h = 3.5 + len(de_lines) * 2.9 + len(en_lines) * 2.6 + 1.5
    page.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="#FFF4E6" stroke="#E8590C" stroke-width="0.35"/>')
    tx, ty = x + 5, y + 4
    page.add(f'<path d="M{tx},{ty - 2.6} L{tx + 3.2},{ty + 3} L{tx - 3.2},{ty + 3} Z" fill="#E8590C"/>')
    page.text(tx, ty + 2.4, "!", 6.5, weight=800, fill="#FFFFFF", anchor="middle")
    ty = y + 3.5 + 1.6
    for line in de_lines:
        page.text(x + 10, ty, line, size, weight=700)
        ty += 2.9
    for line in en_lines:
        page.text(x + 10, ty, line, size * 0.9, fill=EN_GREY)
        ty += 2.6
    return h


def draw_qr(page: Page, x: float, y: float, s: float, topic: str) -> None:
    try:
        import segno
    except ImportError:
        sys.exit("QR codes need segno: python3 -m pip install --user segno")
    qr = segno.make(qr_url(topic), error="m", micro=False)
    rows = list(qr.matrix)
    n = len(rows)
    m = s / (n + 2)  # one-module quiet zone inside the box
    d = "".join(f"M{x + (c + 1) * m:.3f},{y + (r + 1) * m:.3f}h{m:.3f}v{m:.3f}h-{m:.3f}z"
                for r, row in enumerate(rows) for c, v in enumerate(row) if v)
    page.add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#fff"/><path d="{d}" fill="{INK}"/>')


def draw_action_card(page: Page, c: MCard, x: float, y: float) -> None:
    de_t, en_t, band, band_text = TIERS[c.kind]
    page.add(f'<rect x="{x}" y="{y}" width="{MC_W}" height="{MC_H}" fill="#fff" stroke="{CUT}" stroke-width="0.2"/>')
    page.add(f'<rect x="{x}" y="{y}" width="{MC_W}" height="{MC_BAND}" fill="{band}"/>')
    page.text(x + 5, y + 8.6, c.id, 16, weight=800, fill=band_text)
    if c.lot:
        lx = x + 5 + len(c.id) * 3.6 + 2.5
        page.add(f'<rect x="{lx}" y="{y + 3}" width="17" height="6" rx="3" fill="#fff" fill-opacity="0.9"/>')
        page.text(lx + 8.5, y + 7.3, f"LOS {c.lot}", 7.5, weight=800, fill=INK, anchor="middle")
    page.text(x + MC_W - 5, y + 8, de_t.upper(), 9.5, weight=800, fill=band_text, anchor="end", spacing=0.6,
              en=en_t if en_t.lower() != de_t.lower() else "", en_fill=band_text)

    pad, side = 6.0, 32.0
    text_w = MC_W - pad - side
    note_h = 0.0
    if c.note:
        lines = len(wrap(c.note[0], text_w - 13, 6.3, bold=True)) * 2.9
        lines += len(wrap(c.note[1], text_w - 13, 6.3 * 0.9)) * 2.6
        note_h = lines + 5 + 2.5
    sub_h = 0.0
    if c.sub:
        sub_h = len(wrap(c.sub[0], text_w, 10, bold=True)) * 4.6 + len(wrap(c.sub[1], text_w, 7.5)) * 3.4 + 2
    body_h = MC_H - MC_BAND - note_h - sub_h - 2 * pad
    size, de_lines, en_lines = fit_box(c.de, c.en, text_w, body_h, (20, 19, 18, 17, 16, 15, 14, 13, 12))
    ty = draw_text_block(page, x + pad, y + MC_BAND + pad - 1, size, de_lines, en_lines)
    if c.sub:
        ty += 2.5
        for line in wrap(c.sub[0], text_w, 10, bold=True):
            page.text(x + pad, ty, line, 10, weight=700, fill=TEAL)
            ty += 4.6
        for line in wrap(f"({c.sub[1]})", text_w, 7.5):
            page.text(x + pad, ty, line, 7.5, fill=EN_GREY)
            ty += 3.4

    if c.note:
        draw_note(page, x + pad, y + MC_H - pad - note_h + 2.5, text_w, c.note)

    rx = x + MC_W - side
    if c.qr:
        draw_qr(page, rx + 3, y + MC_BAND + 3, 26, c.qr)
    draw_logo_pill(page, x + MC_W / 2 + 4, y + MC_BAND / 2, c.id)
    # pledge-dot corner; centred in the side column when there is no QR
    cx = x + MC_W - side / 2
    cy = y + MC_H - 13 if c.qr else y + MC_BAND + (MC_H - MC_BAND) / 2 + 6
    page.add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#fff" stroke="{INK}" stroke-width="0.4" stroke-dasharray="1.3 1"/>')
    page.text(cx, cy - 13, "Mein Punkt", 6.5, weight=700, anchor="middle")
    page.text(cx, cy - 10.2, "(my dot)", 5.2, fill=EN_GREY, anchor="middle")


def draw_logo_pill(page: Page, cx: float, cy: float, key: str) -> None:
    """White pill with the Circular Munich and IsarPunk marks, for card headers."""
    w, h = 25.0, 8.6
    x, y = cx - w / 2, cy - h / 2
    page.add(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w}" height="{h}" rx="{h / 2}" fill="#fff"/>')
    page.add(embed_svg(CM_MARK, f"pcm-{key}", x + 3.2, y + 1.1, 6.4, 6.4))
    page.add(embed_svg(BRAND_MARK, f"pbm-{key}", x + 11.2, y + 0.6, 11, 7.4))


def draw_cycle(page: Page, cx: float, cy: float, r: float, color: str) -> None:
    """Circularity icon: two clockwise arrows forming a loop."""
    import math

    def pt(a: float, rad: float = r) -> tuple[float, float]:
        t = math.radians(a)
        return cx + rad * math.sin(t), cy - rad * math.cos(t)

    sw, head = r * 0.3, r * 0.42
    for start, end in ((25, 150), (205, 330)):
        (x1, y1), (x2, y2) = pt(start), pt(end)
        page.add(f'<path d="M{x1:.3f},{y1:.3f} A{r},{r} 0 0 1 {x2:.3f},{y2:.3f}" fill="none" '
                 f'stroke="{color}" stroke-width="{sw:.3f}" stroke-linecap="round"/>')
        t = math.radians(end)
        tx, ty = math.cos(t), math.sin(t)          # clockwise tangent
        (ox, oy), (ix, iy) = pt(end, r + head), pt(end, r - head)
        tip = (x2 + tx * head * 1.3, y2 + ty * head * 1.3)
        page.add(f'<polygon points="{ox:.3f},{oy:.3f} {tip[0]:.3f},{tip[1]:.3f} {ix:.3f},{iy:.3f}" fill="{color}"/>')


def draw_flag(page: Page, x: float, y: float, cell: float = 1.8) -> None:
    """Checkered finish flag; (x, y) is the top of the pole."""
    page.add(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 4 * cell + 2}" stroke="{INK}" stroke-width="0.7" stroke-linecap="round"/>')
    page.add(f'<rect x="{x + 0.35}" y="{y}" width="{4 * cell}" height="{3 * cell}" fill="#fff" stroke="{INK}" stroke-width="0.3"/>')
    for r in range(3):
        for col in range(4):
            if (r + col) % 2 == 0:
                page.add(f'<rect x="{x + 0.35 + col * cell}" y="{y + r * cell}" width="{cell}" height="{cell}" fill="{INK}"/>')


def draw_ending_card(page: Page, c: MCard, x: float, y: float) -> None:
    band = 13.0
    page.add(f'<rect x="{x}" y="{y}" width="{MC_W}" height="{MC_H}" fill="#fff" stroke="{CUT}" stroke-width="0.2"/>')
    page.add(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="{MC_W - 3}" height="{MC_H - 3}" rx="3" fill="#FFFDF0" '
             f'stroke="{SUN}" stroke-width="1.4"/>')
    page.add(f'<path d="M{x + 1.5},{y + band} V{y + 4.5} a3,3 0 0 1 3,-3 H{x + MC_W - 4.5} a3,3 0 0 1 3,3 V{y + band} Z" fill="{SUN}"/>')
    draw_flag(page, x + 7, y + 3.4)
    page.text(x + 17, y + 9.6, "ZIEL", 12, weight=800, spacing=1.2, en="ending")
    page.text(x + MC_W - 7, y + 9.8, c.id, 14, weight=800, anchor="end")
    draw_logo_pill(page, x + MC_W / 2 + 6, y + 7.2, c.id)
    # good (inner-loop) endings carry the circularity icon; others have no mark
    pad, top, foot = 10.0, band + 2, (19.0 if c.cm else 5.0)
    size, de_lines, en_lines = fit_box(c.de, c.en, MC_W - 2 * pad, MC_H - top - foot,
                                       (19, 18, 17, 16, 15, 14, 13, 12))
    block = block_height(size, de_lines, en_lines)
    draw_text_block(page, x + MC_W / 2, y + top + (MC_H - top - foot - block) / 2, size, de_lines, en_lines,
                    anchor="middle")
    if c.cm:
        draw_cycle(page, x + MC_W / 2, y + MC_H - 11, 5.2, GREEN)


def draw_start_card(page: Page, c: MCard, x: float, y: float, w: float, h: float, label: tuple[str, str]) -> None:
    page.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{TEAL}" stroke="{CUT}" stroke-width="0.2"/>')
    page.add(f'<rect x="{x}" y="{y}" width="{w}" height="16" fill="#003B53"/>')
    page.add(f'<rect x="{x}" y="{y + 16}" width="{w}" height="1.4" fill="{SUN}"/>')
    page.text(x + 8, y + 11.2, c.id, 18, weight=800, fill=SUN)
    page.text(x + w - 8, y + 11.2, label[0], 15, weight=800, fill="#FFFFFF", anchor="end", spacing=1.5,
              en=label[1], en_fill="#BFD9E4")
    draw_logo_pill(page, x + w / 2, y + 8, f"{c.id}{y:.0f}")
    pad = 12.0
    box_w, box_h = w - 2 * pad, h - 16 - 2 * 6
    size, de_lines, en_lines = fit_box(c.de, c.en, box_w, box_h, (26, 24, 22, 20, 18, 16))
    block = block_height(size, de_lines, en_lines)
    draw_text_block(page, x + pad, y + 16 + 6 + (box_h - block) / 2, size, de_lines, en_lines,
                    fill="#FFFFFF", en_fill="#BFD9E4")


def draw_star(page: Page, cx: float, cy: float, r: float, fill: str) -> None:
    import math
    pts = " ".join(f"{cx + (r if i % 2 == 0 else r * 0.42) * math.sin(i * math.pi / 5):.3f},"
                   f"{cy - (r if i % 2 == 0 else r * 0.42) * math.cos(i * math.pi / 5):.3f}" for i in range(10))
    page.add(f'<polygon points="{pts}" fill="{fill}"/>')


def draw_joker_card(page: Page, x: float, y: float) -> None:
    """Blank wild card: teams write their own action on it."""
    page.add(f'<rect x="{x}" y="{y}" width="{MC_W}" height="{MC_H}" fill="#fff" stroke="{CUT}" stroke-width="0.2"/>')
    colours = JOKER_COLOURS
    seg = MC_W / len(colours)
    for i, col in enumerate(colours):
        page.add(f'<rect x="{x + i * seg:.3f}" y="{y}" width="{seg + 0.05:.3f}" height="{MC_BAND}" fill="{col}"/>')
    page.add(f'<rect x="{x + 4}" y="{y + 2.2}" width="52" height="{MC_BAND - 4.4}" rx="3.8" fill="{INK}"/>')
    draw_star(page, x + 10, y + MC_BAND / 2, 3.4, SUN)
    page.text(x + 15.5, y + 8.4, "JOKER", 11, weight=800, fill="#FFFFFF", spacing=0.8,
              en="wild card", en_fill="#C9D3DA")

    pad, side = 6.0, 32.0
    page.text(x + pad, y + MC_BAND + 8, "Eure eigene Aktion:", 13, weight=700, en="your own action")
    for i in range(4):
        ly = y + MC_BAND + 19 + i * 11
        page.add(f'<line x1="{x + pad}" y1="{ly}" x2="{x + MC_W - side - 2}" y2="{ly}" stroke="{CUT}" stroke-width="0.35"/>')

    rx = x + MC_W - side
    draw_logo_pill(page, x + MC_W - 18, y + MC_BAND / 2, f"joker{x:.0f}-{y:.0f}")
    cx, cy = x + MC_W - side / 2, y + MC_BAND + (MC_H - MC_BAND) / 2 + 6
    page.add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#fff" stroke="{INK}" stroke-width="0.4" stroke-dasharray="1.3 1"/>')
    page.text(cx, cy - 13, "Mein Punkt", 6.5, weight=700, anchor="middle")
    page.text(cx, cy - 10.2, "(my dot)", 5.2, fill=EN_GREY, anchor="middle")


def card_sheets(cards: list[MCard], title: tuple[str, str], sub: tuple[str, str], draw,
                joker: bool = False, jokers: int = 0) -> list[Page]:
    """4 cards per landscape sheet; `jokers` are appended, `joker` fills leftover slots."""
    items: list = list(cards) + [None] * jokers
    pages = []
    for start in range(0, len(items), 4):
        page = Page(landscape=True)
        page_header(page, title, sub)
        chunk = items[start:start + 4]
        for i in range(4):
            row, col = divmod(i, 2)
            x, y = MC_X0 + col * MC_W, MC_Y0 + row * MC_H
            if i < len(chunk):
                if chunk[i] is None:
                    draw_joker_card(page, x, y)
                else:
                    draw(page, chunk[i], x, y)
            elif joker:
                draw_joker_card(page, x, y)
        page_footer(page)
        pages.append(page)
    return pages


def start_sheet(c: MCard, title: tuple[str, str], sub: tuple[str, str], label: tuple[str, str]) -> Page:
    page = Page(landscape=True)
    page_header(page, title, sub)
    for row in range(2):
        draw_start_card(page, c, MC_X0, MC_Y0 + row * MC_H, 2 * MC_W, MC_H, label)
    page_footer(page)
    return page


# ---------------------------------------------------------------- Mission 1: Save Oma

M1_START = MCard("S1", "Omas PC läuft Windows 10. Der Sicherheits-Countdown bis Oktober 2027 läuft. "
                       "Sie weiß noch nichts davon.",
                 "Oma's PC runs Windows 10. The security countdown to October 2027 is running. "
                 "She does not know yet.", "start")

M1_ENDINGS = [
    MCard("O1", "Omas PC läuft mit Linux — sicher — und sie benutzt ihn weiter.",
          "Runs Linux safely; she keeps using it.", "ending", cm=True),
    MCard("O2", "Ein Repair-Shop hat Omas PC umgestellt.", "A repair shop switched it over.", "ending", cm=True),
    MCard("O3", "Nichts passiert. Omas PC ist online — und unsicher.", "Nothing happens; online and unsafe.", "ending"),
    MCard("O4", "Oma kauft einen neuen PC, den sie nicht gebraucht hätte. Der alte landet im Müll.",
          "Buys a new PC she didn't need; the old one is binned.", "ending"),
    MCard("O5", "Oma fällt auf eine Betrugsmasche rein.", "Falls for a scam.", "ending"),
    MCard("O6", "Oma traut sich nicht mehr an den Computer und benutzt ihn gar nicht mehr.",
          "Too scared; stops using it altogether.", "ending"),
]

M1_ACTIONS = [
    MCard("C1", "Frag Oma/Opa, welches Windows auf ihrem PC läuft.", "Ask which Windows is on their PC.", "talk"),
    MCard("C2", "Erklär jemandem zu Hause, was im Oktober 2027 passiert.",
          "Explain what happens in October 2027.", "talk"),
    MCard("C3", "Schau nach, ob der PC noch Updates bekommt.", "Check whether it still gets updates.", "check"),
    MCard("C4", "Finde heraus, ob der PC überhaupt Windows 11 kann.",
          "Find out whether it could run Windows 11.", "check"),
    MCard("C5", "Erzähl es einer Person außerhalb dieses Raums.", "Tell one person outside this room.", "talk"),
    MCard("C6", "Sichere zuerst Omas Fotos.", "Back up Oma's photos first.", "safety"),
    MCard("C7", "Lade ein Linux-Image herunter — z.B. Linux Mint.", "Download a Linux image.", "do", qr="iso"),
    MCard("C8", "Mach aus einem alten USB-Stick einen Live-Stick.", "Turn an old USB stick into a live stick.",
          "do", qr="stick", note=LIVE_USB_WARNING),
    MCard("C9", "Finde heraus, mit welcher Taste dein Computer ins Boot-Menü kommt.",
          "Find your computer's boot-menu key.", "do", qr="boot"),
    MCard("C10", "Setz dich mit Oma hin und zeig ihr den Live-Stick — nichts wird verändert.",
          "Sit with Oma and show her the live stick.", "do"),
    MCard("C11", "Frag eine KI, was man mit diesem PC machen kann — und prüfe die Antwort.",
          "Ask an AI what can be done with this PC — and check the answer.", "learn"),
    MCard("C12", "Such ein Tutorial und schau es dir an.", "Find a tutorial and watch it.", "learn", qr="lernen"),
    MCard("C13", "Frag jemanden in der Schule, der sich auskennt.", "Ask someone at school who knows.", "learn"),
    MCard("C14", "Bring den PC in einen Repair-Shop und frag, was möglich ist.",
          "Take the PC to a repair shop and ask.", "shop"),
    MCard("C15", "Installiere Linux — zusammen mit einer erwachsenen Person, nach dem Backup und mit Erlaubnis.",
          "Install Linux — with an adult, after a backup and with permission.", "do"),
]


def build_mission1() -> Path:
    t = ("Mission 1 — Rettet Omas PC", "Save Oma")
    pages = [start_sheet(M1_START, t, ("Start S1 · 2 pro Blatt · 2× drucken für 4 Teams",
                                        "starter S1 · 2 per sheet · print 2× for 4 teams"),
                         ("START", "problem"))]
    pages += card_sheets(M1_ENDINGS, t, ("Ziele O1–O6 + Joker · 1 Set pro Team · Ziele laminieren, keine Punkte",
                                         "endings O1–O6 + wild cards · 1 set per team · laminate endings, no dots"),
                         draw_ending_card, joker=True)
    pages += card_sheets(M1_ACTIONS, t, ("Aktionen C1–C15 + Joker · 1 Set pro Team · Verbrauchsmaterial",
                                         "actions C1–C15 + wild card · 1 set per team · consumable"),
                         draw_action_card, joker=True)
    return export_pdf(pages, "M1_Mission1_Cards")


# ---------------------------------------------------------------- Mission 2: IsarPunk

M2_START = MCard("S2", "Bei IsarPunk handeln und lernen wir: Wie können wir verhindern, dass ein Gerät im Müll landet?",
                 "At IsarPunk, we act and learn: How can we keep a device from ending up in the bin?", "start")

M2_ENDINGS = [
    MCard("H1", "Das Gerät läuft wieder — mit Linux — und jemand benutzt es.",
          "Works again with Linux; someone uses it.", "ending", cm=True),
    MCard("H2", "Ein Repair-Shop hat es repariert oder umgestellt.", "A shop repaired or switched it.", "ending", cm=True),
    MCard("H3", "Daraus ist ein Projekt geworden — Konsole, Medienserver, Chat-Server.",
          "It became a project.", "ending", cm=True),
    MCard("H4", "Jemand anders nutzt jetzt das Gerät oder brauchbare Teile daraus — verkauft oder verschenkt.",
          "Someone else uses the device or usable parts from it — sold or given away.", "ending", cm=True),
    MCard("H5", "Jemand in der Familie hat jetzt einen Computer, der vorher keinen hatte.",
          "A family member who had no computer now has one.", "ending", cm=True),
    MCard("H6", "Die Materialien wurden richtig verwertet.", "The materials were properly recovered.", "ending"),
    MCard("H7", "Es liegt weiter im Schrank.", "It stays in the cupboard.", "ending"),
    MCard("H8", "Es landet im Hausmüll.", "It goes in the household bin.", "ending"),
]

M2_ACTIONS = [
    # Lot A — discover and learn
    MCard("D1", "Such in der Wohnung nach einem Gerät, das niemand mehr benutzt.",
          "Hunt the house for an unused device.", "find", lot="A"),
    MCard("D2", "Frag Nachbarn oder Oma, ob noch was im Schrank liegt.", "Ask a neighbour or Oma.", "find", lot="A"),
    MCard("D3", "Finde heraus, wie alt es ist und was drin steckt.", "Find out its age and what is inside.",
          "diagnose", lot="A"),
    MCard("D4", "Lern-Karte: Linux lernen", "Learn Linux", "learn", lot="A", qr="lernen"),
    MCard("D5", "Lern-Karte: Von USB booten", "Learn how to boot from USB", "learn", lot="A", qr="boot"),
    # Lot B — safety and practical action
    MCard("D6", "Sichere die Daten, bevor du irgendwas machst.", "Back up the data before anything else.",
          "safety", lot="B", note=SAFETY_RULES),
    MCard("D7", "Mach aus einem alten USB-Stick einen bootfähigen Linux-Stick.",
          "Turn an old USB stick into a bootable Linux stick.", "revive", lot="B", qr="stick", note=LIVE_USB_WARNING),
    MCard("D8", "Probier einen Live-USB-Stick daran aus.", "Try a live USB stick on it.", "revive", lot="B",
          note=SAFETY_RULES),
    MCard("D9", "Installiere Linux — zusammen mit einem Erwachsenen.", "Install Linux together with an adult.",
          "revive", lot="B", note=SAFETY_RULES),
    MCard("D10", "Bau mehr RAM oder eine SSD ein.", "Fit more RAM or an SSD.", "revive", lot="B", note=SAFETY_RULES),
    MCard("D11", "Bring es zu einem Repair-Shop oder Repair-Café von unserer Liste.",
          "Take it to a listed shop or café.", "shop", lot="B", note=SAFETY_RULES),
    MCard("D12", "Gib es an ein jüngeres Geschwisterkind oder an Oma weiter.",
          "Pass it to a younger sibling or to Oma.", "family", lot="B"),
    MCard("D13", "Verkauf es oder verschenk es (eBay, Kleinanzeigen).", "Sell it or give it away.", "passon", lot="B"),
    MCard("D14", "Bring ein wirklich totes Gerät zum Wertstoffhof — nicht in den Hausmüll.",
          "Take a truly dead device to the Wertstoffhof.", "recycle", lot="B"),
    MCard("D15", "Verkaufe brauchbare Einzelteile (RAM, Festplatte).", "Sell usable parts.", "recover", lot="B"),
    # Lot C — optional projects, revealed last
    MCard("D16", "Entertainment-Projekte", "entertainment projects", "project", lot="C", qr="unterhaltung",
          sub=("Batocera / RetroPie · Jellyfin / Navidrome · OBS", "retro games · media server · streaming")),
    MCard("D17", "Sicherheit & Privatsphäre", "security & privacy", "project", lot="C", qr="privatsphaere",
          sub=("Pi-hole · Nextcloud · Vaultwarden", "ad blocker · own cloud · password manager")),
    MCard("D18", "Eigener Chat-Server für eure Gruppe", "own chat server for your group", "project", lot="C",
          qr="chat", sub=("Matrix / Synapse — nur mit Erwachsenen und nach Schulregeln",
                          "only with adults and following school rules")),
    MCard("D19", "Projekt-Anleitungen", "project guides", "project", lot="C", qr="projekte",
          sub=("Pi-hole, Jellyfin, Nextcloud, Batocera", "step-by-step videos")),
]


def build_mission2() -> Path:
    t = ("Mission 2 — IsarPunk", "")
    pages = [start_sheet(M2_START, t, ("Mission S2 · 2 pro Blatt · 2× drucken für 4 Teams",
                                        "goal S2 · 2 per sheet · print 2× for 4 teams"),
                         ("MISSION", "goal"))]
    pages += card_sheets(M2_ENDINGS, t, ("Ziele H1–H8 · 1 Set pro Team · laminieren, keine Punkte",
                                         "endings H1–H8 · 1 set per team · laminate, no dots"), draw_ending_card)
    pages += card_sheets(M2_ACTIONS, t, ("Aktionen D1–D19 (Los A, B, C) + 5 Joker · 1 Set pro Team · Verbrauchsmaterial",
                                         "actions D1–D19 (lots A, B, C) + 5 wild cards · 1 set per team · consumable"),
                         draw_action_card, jokers=5)
    return export_pdf(pages, "M2_Mission2_Cards")


# ---------------------------------------------------------------- GitHub Pages link page (QR targets)

PAGE_CSS = """
:root{--teal:#005577;--sun:#F5D400;--ink:#1D2B36;--grey:#5F7280;--bg:#F4F8FA}
*{box-sizing:border-box}body{margin:0;font-family:'Open Sans','Noto Sans',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.45}
header{background:var(--teal);color:#fff;padding:18px 16px;display:flex;align-items:center;gap:14px;border-bottom:5px solid var(--sun)}
header img{height:52px;background:#fff;border-radius:10px;padding:4px}header h1{margin:0;font-size:1.4rem}
.en{color:var(--grey);font-size:.82em;font-weight:400}header .en{color:#BFD9E4}
main{max-width:720px;margin:0 auto;padding:12px}
section{background:#fff;border-radius:12px;padding:14px 16px;margin:14px 0;border:1px solid #D5DDE3;scroll-margin-top:10px}
section:target{outline:4px solid var(--sun)}
h2{margin:0 0 4px;font-size:1.2rem;color:var(--teal)}.cards{font-size:.75rem;color:var(--grey);font-weight:700}
ul{list-style:none;padding:0;margin:10px 0 0}li{margin:8px 0}
a.btn{display:block;padding:12px 14px;border-radius:10px;background:var(--bg);color:var(--ink);text-decoration:none;border:1px solid #D5DDE3}
a.btn:hover{border-color:var(--teal)}a.btn b{display:block}.meta{font-size:.8rem;color:var(--grey)}
.tag{display:inline-block;font-size:.7rem;font-weight:700;padding:1px 7px;border-radius:6px;margin-right:6px;color:#fff;background:#E03131}
.tag.web{background:var(--teal)}
footer{text-align:center;font-size:.75rem;color:var(--grey);padding:20px 12px 30px}footer img{height:34px;vertical-align:middle;margin:0 6px}
"""


def build_pages() -> Path:
    DOCS.mkdir(exist_ok=True)
    shutil.copy(BRAND_MARK, DOCS / "isarpunk.svg")
    shutil.copy(CM_MARK, DOCS / "circular-munich.svg")
    (DOCS / ".nojekyll").write_text("")
    e = html.escape
    sections = []
    for key, t in QR_TOPICS.items():
        items = []
        for kind, de, en, url, note in t["links"]:
            tag = {"video": '<span class="tag">YouTube</span>',
                   "section": '<span class="tag web">Mehr</span>'}.get(kind, '<span class="tag web">Web</span>')
            target = "" if url.startswith("#") else ' target="_blank" rel="noopener"'
            en_html = f' <span class="en">({e(en)})</span>' if en else ""
            meta = f'<span class="meta">{e(note)}</span>' if note else ""
            items.append(f'<li><a class="btn" href="{e(url)}"{target}>'
                         f'<b>{tag}{e(de)}{en_html}</b>{meta}</a></li>')
        cards = f'<div class="cards">Karte {e(t["cards"])}</div>' if t["cards"] else ""
        sections.append(
            f'<section id="{key}">{cards}<h2>{e(t["title"][0])} <span class="en">({e(t["title"][1])})</span></h2>'
            f'<p>{e(t["intro"][0])} <span class="en">({e(t["intro"][1])})</span></p><ul>{"".join(items)}</ul></section>')
    page = f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IsarPunk — Links aus dem Workshop</title><meta name="robots" content="noindex">
<style>{PAGE_CSS}</style></head><body>
<header><img src="isarpunk.svg" alt="IsarPunk"><div><h1>IsarPunk — Links aus dem Workshop</h1>
<div class="en">(links from the workshop)</div></div></header>
<main>{"".join(sections)}</main>
<footer><img src="isarpunk.svg" alt="IsarPunk"><img src="circular-munich.svg" alt="Circular Munich"><br>
© 2026 Circular Munich e.V. &amp; Peter Balogh — alle Rechte vorbehalten <span class="en">(all rights reserved)</span><br>
Videos und Seiten gehören ihren Urheber:innen <span class="en">(videos and pages belong to their creators)</span></footer>
</body></html>
"""
    target = DOCS / "index.html"
    target.write_text(page, encoding="utf-8")
    return target


# ---------------------------------------------------------------- main

ARTIFACTS = {
    "pages": build_pages,
    "layer-sort": build_layer_sort,
    "stations": build_stations,
    "measure": build_measure,
    "mission1": build_mission1,
    "mission2": build_mission2,
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artifacts", nargs="*", help=f"any of: {', '.join(ARTIFACTS)} (default: all)")
    ap.add_argument("--refresh", action="store_true", help="re-download logos")
    args = ap.parse_args()
    unknown = set(args.artifacts) - set(ARTIFACTS)
    if unknown:
        ap.error(f"unknown artifact(s): {', '.join(sorted(unknown))}")

    fetch_logos(args.refresh)
    for name in args.artifacts or ARTIFACTS:
        print(f"  built {ARTIFACTS[name]()}")


if __name__ == "__main__":
    main()
