"""Builds assets/hero.svg and assets/footer.svg: a matatu-livery banner.

Lettering is converted to paths, so the SVGs need no web fonts (GitHub
serves README images with external loading blocked). Run once after edits:

    curl -sfLO https://github.com/google/fonts/raw/main/ofl/bungee/Bungee-Regular.ttf
    python3 .github/scripts/hero.py Bungee-Regular.ttf
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT = TTFont(sys.argv[1])
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT["head"].unitsPerEm
OUT = Path(__file__).resolve().parents[2] / "assets"

INDIGO, INDIGO_DEEP, YELLOW, PINK, CYAN, AMBER, CHROME = (
    "#1B1446", "#110C30", "#FFD23F", "#FF3E8A", "#2EC4E6", "#FFB000", "#F4F6FF")


def text_path(text, x, baseline, size, tracking=0.0):
    """Return (svg path markup, advance width) for text set in the font."""
    scale = size / UPM
    parts, cursor = [], x
    for ch in text:
        name = CMAP.get(ord(ch))
        if name is None:
            continue
        glyph = GLYPHS[name]
        pen = SVGPathPen(GLYPHS)
        glyph.draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path transform="translate({cursor:.1f} {baseline}) scale({scale:.5f} {-scale:.5f})" d="{d}"/>')
        cursor += glyph.width * scale + tracking
    return "".join(parts), cursor - x - tracking


# 5x7 dot-matrix glyphs for the LED route board, one string per row.
DOTS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    " ": ["00000"] * 7,
}
PITCH, R = 7.0, 2.6


def led_text(text, x, y, color):
    dots = []
    for i, ch in enumerate(text):
        for row, bits in enumerate(DOTS[ch]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    cx, cy = x + (i * 6 + col) * PITCH, y + row * PITCH
                    dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R}"/>')
    return f'<g fill="{color}" filter="url(#glow)">{"".join(dots)}</g>'


def led_board(x, y, cols, route, stops):
    """A black board with unlit dots, a fixed route number and cycling stops."""
    w, h = cols * PITCH + 28, 7 * PITCH + 28
    unlit = "".join(
        f'<circle cx="{x + 14 + c * PITCH:.1f}" cy="{y + 14 + r * PITCH:.1f}" r="{R}"/>'
        for r in range(7) for c in range(cols))
    route_dots = led_text(route, x + 14, y + 14, PINK)
    stop_x = x + 14 + (len(route) * 6 + 2) * PITCH
    n, cycle = len(stops), len(stops) * 2.2
    groups = []
    for i, stop in enumerate(stops):
        # Discrete SMIL timing: stop i is lit for its own slice of the cycle.
        if i == 0:
            times, values = f"0;{1 / n:.4f};1", "1;0;0"
        else:
            times, values = f"0;{i / n:.4f};{(i + 1) / n:.4f};1", "0;1;0;0"
        groups.append(
            f'<g opacity="{1 if i == 0 else 0}"><animate attributeName="opacity" calcMode="discrete" '
            f'dur="{cycle:.1f}s" repeatCount="indefinite" keyTimes="{times}" values="{values}"/>'
            f'{led_text(stop, stop_x, y + 14, AMBER)}</g>')
    return f"""
<rect x="{x - 6}" y="{y - 6}" width="{w + 12}" height="{h + 12}" rx="12" fill="url(#chrome)"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#07060F"/>
<g fill="#1E1A2E">{unlit}</g>
{route_dots}
<g>{"".join(groups)}</g>"""


def defs():
    return f"""<defs>
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2A1F6E"/><stop offset=".55" stop-color="{INDIGO}"/><stop offset="1" stop-color="{INDIGO_DEEP}"/>
  </linearGradient>
  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#B9BED6"/>
    <stop offset=".5" stop-color="#6E7391"/><stop offset="1" stop-color="#E3E6F5"/>
  </linearGradient>
  <linearGradient id="paint" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFF6C2"/><stop offset=".46" stop-color="{YELLOW}"/>
    <stop offset=".54" stop-color="#FF9F1C"/><stop offset="1" stop-color="#FFC93C"/>
  </linearGradient>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="1.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""


def stripes(x0, width, height):
    """Diagonal racing stripes sweeping up to the right."""
    bands = [(0, 110, PINK), (128, 46, YELLOW), (190, 20, CYAN), (226, 9, CHROME)]
    out = []
    for off, w, color in bands:
        a, b = x0 + off, x0 + off + w
        out.append(f'<polygon points="{a},{height} {b},{height} {b + 260},0 {a + 260},0" fill="{color}"/>')
    return f'<g transform="translate({width - x0 - 560} 0)">{"".join(out)}</g>'


def rivets(width, y):
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="3.2" fill="url(#chrome)"/>' for x in range(24, width, 48))


def hero():
    W, H = 1280, 440
    first, w_first = text_path("LEVI", 0, 0, 132, 6)
    last, w_last = text_path("OPUNGA", 0, 0, 132, 6)
    slogan, w_slogan = text_path("ALL SCREENS, ONE CODEBASE", 0, 0, 22, 2.5)

    def lettering(paths, x, y):
        return f"""<g transform="translate({x} {y})">
  <g fill="{PINK}" transform="translate(9 9)">{paths}</g>
  <g fill="{INDIGO_DEEP}" stroke="{INDIGO_DEEP}" stroke-width="14" stroke-linejoin="round">{paths}</g>
  <g fill="url(#paint)" stroke="{CHROME}" stroke-width="2.5" stroke-linejoin="round">{paths}</g>
</g>"""

    board = led_board(56, 46, 63, "254", ["ANDROID", "IOS", "MACOS", "WINDOWS", "LINUX", "WEB"])
    ribbon_w = w_slogan + 48
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Levi Opunga</title>
<desc id="d">A matatu-style painted banner. The LED route board reads 254 and cycles through Android, iOS, macOS, Windows, Linux and Web. The slogan reads: all screens, one codebase.</desc>
{defs()}
<rect width="{W}" height="{H}" rx="18" fill="url(#panel)"/>
<clipPath id="body"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<g clip-path="url(#body)">
  {stripes(0, W, H)}
  <rect y="0" width="{W}" height="10" fill="url(#chrome)"/>
  <rect y="{H - 26}" width="{W}" height="26" fill="url(#chrome)"/>
  {rivets(W, 22)}
</g>
{board}
{lettering(first, 52, 250)}
{lettering(last, 52, 372)}
<g transform="translate({W - ribbon_w - 40} {H - 78})">
  <rect width="{ribbon_w}" height="40" rx="6" fill="{INDIGO_DEEP}" stroke="{YELLOW}" stroke-width="2"/>
  <g fill="{CHROME}" transform="translate(24 31)">{slogan}</g>
</g>
</svg>
"""


def footer():
    W, H = 1280, 120
    line, w = text_path("FOLLOW ME ON X: @BADATVIM", 0, 0, 30, 3)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Follow @badAtVim on X">
{defs()}
<clipPath id="body"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<g clip-path="url(#body)">
  <rect width="{W}" height="{H}" fill="url(#panel)"/>
  {stripes(-180, W, H)}
  <rect width="{W}" height="8" fill="url(#chrome)"/>
</g>
<g transform="translate(56 {H / 2 + 14})">
  <g fill="{PINK}" transform="translate(4 4)">{line}</g>
  <g fill="url(#paint)">{line}</g>
</g>
</svg>
"""


OUT.mkdir(exist_ok=True)
(OUT / "hero.svg").write_text(hero())
(OUT / "footer.svg").write_text(footer())
print("wrote", OUT / "hero.svg", OUT / "footer.svg")
