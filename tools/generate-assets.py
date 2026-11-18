#!/usr/bin/env python3
"""
Generates the GitHub profile header plates (dark + light) and the OG image.

All type is converted to SVG paths so the artwork renders identically on
GitHub, where external fonts inside an <img>-served SVG are not available.
Translucent colors are pre-blended onto the paper so every renderer agrees.

Usage:
    python3 -m venv .venv && .venv/bin/pip install fonttools
    .venv/bin/python tools/generate-assets.py
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
ASSETS = ROOT / "assets"

SANS = FONTS / "SpaceGrotesk.ttf"
MONO = FONTS / "JetBrainsMono.ttf"

THEMES = {
    "dark": {
        "paper": "#0D1117",
        "ink": "#E8E6E1",
        "muted": "#8A929C",
        "dim": "#6E7681",
        "rule": "#232A31",
        "accent": "#FFB020",
    },
    "light": {
        "paper": "#FFFFFF",
        "ink": "#14171A",
        "muted": "#525A64",
        "dim": "#6E6862",
        "rule": "#E1DCD2",
        "accent": "#A85F00",
    },
}

INDEX = ["WORK", "STACK", "METHOD", "RECORD", "CONTACT"]

_font_cache: dict[tuple[str, int], TTFont] = {}


def mix(bg: str, fg: str, alpha: float) -> str:
    b = [int(bg[i : i + 2], 16) for i in (1, 3, 5)]
    f = [int(fg[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * alpha):02X}" for x, y in zip(b, f))


def load_font(path: Path, weight: int) -> TTFont:
    key = (str(path), weight)
    if key not in _font_cache:
        _font_cache[key] = instantiateVariableFont(TTFont(path), {"wght": weight})
    return _font_cache[key]


def text_width(font: TTFont, text: str, size: float, tracking: float = 0.0) -> float:
    upem = font["head"].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    total = 0.0
    for char in text:
        name = cmap.get(ord(char))
        total += (glyphs[name].width * scale if name else size * 0.3) + tracking
    return max(total - tracking, 0.0)


def text_paths(font, text, size, x, y, tracking=0.0) -> tuple[str, float]:
    upem = font["head"].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    parts: list[str] = []
    pen_x = 0.0
    for char in text:
        name = cmap.get(ord(char))
        if name is None:
            pen_x += size * 0.3 + tracking
            continue
        outline = SVGPathPen(glyphs)
        glyphs[name].draw(
            TransformPen(outline, Transform(scale, 0, 0, -scale, x + pen_x, y))
        )
        commands = outline.getCommands()
        if commands:
            parts.append(commands)
        pen_x += glyphs[name].width * scale + tracking
    return "".join(parts), pen_x - tracking


def put(font, text, size, x, y, fill, tracking=0.0, anchor="start"):
    width = text_width(font, text, size, tracking)
    if anchor == "end":
        x -= width
    elif anchor == "middle":
        x -= width / 2
    commands, _ = text_paths(font, text, size, x, y, tracking)
    return f'<path d="{commands}" fill="{fill}"/>'


def grid(w, h, color, step=8, pad=16):
    lines = [f'<path d="M{pad} {y}H{w - pad}" stroke="{color}" fill="none"/>'
             for y in range(step, h - 8, step)]
    return "".join(lines)


def crop_marks(w, h, color, accent, inset=20, length=14):
    coords = [
        (inset, inset, 1, 1, accent),
        (w - inset, inset, -1, 1, color),
        (inset, h - inset, 1, -1, color),
        (w - inset, h - inset, -1, -1, color),
    ]
    return "".join(
        f'<path d="M{x} {y + dy * length}V{y}H{x + dx * length}" '
        f'stroke="{stroke}" stroke-width="1" fill="none"/>'
        for x, y, dx, dy, stroke in coords
    )


def header_svg(theme):
    t = THEMES[theme]
    w, h = 1000, 340
    sans_600 = load_font(SANS, 600)
    sans_500 = load_font(SANS, 500)
    mono_400 = load_font(MONO, 400)
    mono_500 = load_font(MONO, 500)

    rule_x = 636
    idx_x = 664
    label_x = 702
    dots_from = 776
    dots_to = 940

    rows = []
    for i, label in enumerate(INDEX, start=1):
        y = 100 + (i - 1) * 33
        rows.append(put(mono_500, f"{i:02d}", 11.5, idx_x, y, t["accent"], 1.2))
        rows.append(put(mono_400, label, 11.5, label_x, y, t["ink"], 1.6))
        dots = "".join(
            f'<circle cx="{x}" cy="{y - 4}" r=".9"/>' for x in range(dots_from, dots_to, 7)
        )
        rows.append(f'<g fill="{mix(t["paper"], t["muted"], .55)}">{dots}</g>')

    available = "OPEN TO BACKEND ROLES"
    avail_w = text_width(mono_400, available, 11.5, 1.5)
    sep_x = 64 + avail_w + 22
    rest_x = sep_x + 16

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
<title id="t">Duban Zuluaga — Backend &amp; Fullstack Engineer</title>
<desc id="d">Profile plate: name, role, availability, and an index of the five sections of this dossier.</desc>
<rect width="{w}" height="{h}" fill="{t["paper"]}"/>
{grid(w, h, mix(t["paper"], t["ink"], .045))}
{crop_marks(w, h, mix(t["paper"], t["dim"], .7), mix(t["paper"], t["accent"], .7))}
<path d="M34 48V306" stroke="{t["rule"]}" fill="none"/>
<path d="M{rule_x} 48V306" stroke="{t["rule"]}" fill="none"/>
{put(mono_500, "//", 12, 48, 66, t["accent"], 2.2)}
{put(mono_400, "PROFILE", 12, 72, 66, t["muted"], 2.6)}
{put(sans_600, "DUBAN", 76, 46, 158, t["ink"], -2)}
{put(sans_600, "ZULUAGA", 76, 46, 234, t["ink"], -2)}
{put(sans_500, "Backend & Fullstack Engineer", 19, 48, 274, t["muted"], 0)}
<circle cx="53" cy="302" r="3.2" fill="{t["accent"]}"/>
{put(mono_400, available, 11.5, 64, 306, t["muted"], 1.5)}
<path d="M{sep_x} 298v10" stroke="{t["dim"]}" fill="none"/>
{put(mono_400, "COLOMBIA · GMT-5 · REMOTE", 11.5, rest_x, 306, t["dim"], 1.5)}
{put(mono_400, "INDEX", 11, idx_x, 66, t["dim"], 2.6)}
{"".join(rows)}
{put(mono_400, "REV 2026.11", 11, 954, 306, t["dim"], 1.5, "end")}
</svg>
"""


def og_svg(theme):
    t = THEMES[theme]
    w, h = 1280, 640
    sans_600 = load_font(SANS, 600)
    sans_500 = load_font(SANS, 500)
    mono_400 = load_font(MONO, 400)
    mono_500 = load_font(MONO, 500)

    rows = []
    for i, label in enumerate(INDEX, start=1):
        y = 190 + (i - 1) * 62
        rows.append(put(mono_500, f"{i:02d}", 20, 888, y, t["accent"], 2))
        rows.append(put(mono_400, label, 20, 948, y, t["ink"], 2.6))
        dots = "".join(
            f'<circle cx="{x}" cy="{y - 7}" r="1.5"/>' for x in range(1072, 1180, 12)
        )
        rows.append(f'<g fill="{mix(t["paper"], t["muted"], .55)}">{dots}</g>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
<title id="t">Duban Zuluaga — Backend &amp; Fullstack Engineer</title>
<desc id="d">Social preview: name, role, stack, availability and section index.</desc>
<rect width="{w}" height="{h}" fill="{t["paper"]}"/>
{grid(w, h, mix(t["paper"], t["ink"], .05), pad=34)}
{crop_marks(w, h, mix(t["paper"], t["dim"], .7), mix(t["paper"], t["accent"], .7), inset=28, length=16)}
<path d="M44 80V560" stroke="{t["rule"]}" fill="none"/>
<path d="M860 80V560" stroke="{t["rule"]}" fill="none"/>
{put(mono_500, "//", 18, 80, 120, t["accent"], 3)}
{put(mono_400, "PROFILE", 18, 120, 120, t["muted"], 3.4)}
{put(sans_600, "DUBAN", 104, 78, 288, t["ink"], -2.8)}
{put(sans_600, "ZULUAGA", 104, 78, 392, t["ink"], -2.8)}
{put(sans_500, "Backend & Fullstack Engineer", 30, 80, 444, t["muted"], 0)}
{put(mono_400, "JAVA · SPRING BOOT · TYPESCRIPT · KUBERNETES", 17, 80, 500, t["dim"], 2.2)}
<circle cx="86" cy="558" r="5" fill="{t["accent"]}"/>
{put(mono_400, "OPEN TO BACKEND ROLES  ·  COLOMBIA  ·  GMT-5", 16, 102, 563, t["muted"], 1.7)}
{put(mono_400, "INDEX", 18, 888, 120, t["dim"], 3.4)}
{"".join(rows)}
{put(mono_400, "SOYDZ.COM", 16, 1180, 563, t["muted"], 1.9, "end")}
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        (ASSETS / f"header-{theme}.svg").write_text(header_svg(theme), encoding="utf-8")
    (ASSETS / "og.svg").write_text(og_svg("dark"), encoding="utf-8")
    print("wrote assets/header-dark.svg, assets/header-light.svg, assets/og.svg")


if __name__ == "__main__":
    main()
