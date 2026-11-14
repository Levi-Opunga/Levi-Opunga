"""Builds the README banner and footer in light and dark: white (or graphite)
livery with Kenyan-flag racing stripes.

Lettering is converted to paths so the SVGs need no web fonts (GitHub serves
README images with external loading blocked). Run after edits:

    mkdir fonts && cd fonts
    curl -sfLo BigShouldersDisplay.ttf 'https://github.com/google/fonts/raw/main/ofl/bigshouldersdisplay/BigShouldersDisplay%5Bwght%5D.ttf'
    curl -sfLo BricolageGrotesque.ttf 'https://github.com/google/fonts/raw/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf'
    cd .. && python3 .github/scripts/hero.py fonts
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[2] / "assets"

THEMES = {
    "light": {"paint": "#F3F4F6", "ink": "#000000", "muted": "#4B5563", "black": "#000000",
              "white": "#FFFFFF", "red": "#BB0000", "green": "#006B3F"},
    "dark": {"paint": "#16181C", "ink": "#F5F5F5", "muted": "#9CA3AF", "black": "#000000",
             "white": "#F5F5F5", "red": "#D42222", "green": "#0E8A55"},
}


class Face:
    def __init__(self, file, **axes):
        font = TTFont(FONTS / file)
        if "fvar" in font:
            font = instantiateVariableFont(font, axes)
        self.glyphs, self.cmap, self.upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm

    def path(self, text, size, tracking=0.0):
        """Return (path markup at origin, advance width)."""
        s, x, parts = size / self.upm, 0.0, []
        for ch in text:
            g = self.glyphs[self.cmap[ord(ch)]]
            pen = SVGPathPen(self.glyphs)
            g.draw(pen)
            if pen.getCommands():
                parts.append(f'<path transform="translate({x:.1f} 0) scale({s:.5f} {-s:.5f})" d="{pen.getCommands()}"/>')
            x += g.width * s + tracking
        return "".join(parts), x - tracking


DISPLAY = Face("BigShouldersDisplay.ttf", wght=900)
TEXT = Face("BricolageGrotesque.ttf", wght=450, wdth=100, opsz=18)
TEXT_BOLD = Face("BricolageGrotesque.ttf", wght=700, wdth=100, opsz=18)

PLATFORMS = ["Android", "iOS", "macOS", "Windows", "Linux", "the web"]


def flag_stripes(t, x, height, widths=(34, 8, 34, 8, 34), lean=170):
    """Black, white, red, white, green bands leaning up to the right."""
    colors = [t["black"], t["white"], t["red"], t["white"], t["green"]]
    out = []
    for color, w in zip(colors, widths):
        out.append(f'<polygon points="{x:.1f},{height} {x + w:.1f},{height} {x + w + lean:.1f},0 {x + lean:.1f},0" fill="{color}"/>')
        x += w
    return "".join(out)


def cycling_words(t, x, baseline, size, slot=2.4, fade=0.3):
    """Each platform fades in, holds, and fades out in turn. The first is visible at rest."""
    n, total = len(PLATFORMS), len(PLATFORMS) * slot
    groups = []
    for i, word in enumerate(PLATFORMS):
        start = i * slot
        if i == 0:
            points = [(0, 1), (slot - fade, 1), (slot, 0), (total - fade, 0), (total, 1)]
        else:
            points = [(0, 0), (start, 0), (start + fade, 1), (start + slot - fade, 1), (start + slot, 0)]
            if start + slot < total:
                points.append((total, 0))
        times = ";".join(f"{p / total:.4f}" for p, _ in points)
        values = ";".join(str(v) for _, v in points)
        word_path, _ = TEXT_BOLD.path(word, size)
        groups.append(
            f'<g opacity="{1 if i == 0 else 0}" fill="{t["ink"]}" transform="translate({x:.1f} {baseline})">'
            f'<animate attributeName="opacity" dur="{total:.1f}s" repeatCount="indefinite" keyTimes="{times}" values="{values}"/>'
            f'{word_path}</g>')
    return "".join(groups)


def hero(t):
    W, H = 1280, 400
    name, _ = DISPLAY.path("LEVI OPUNGA", 196, 4)
    lead, lead_w = TEXT.path("Shipping to ", 26)
    tag, _ = TEXT.path("Full-stack engineer in Kenya. All screens, one codebase.", 24)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">Levi Opunga. Shipping to Android, iOS, macOS, Windows, Linux and the web. Full-stack engineer in Kenya.</title>
<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{t["paint"]}"/>
  {flag_stripes(t, 1066, H)}
</g>
<g fill="{t["muted"]}" transform="translate(70 92)">{lead}</g>
{cycling_words(t, 70 + lead_w, 92, 26)}
<g fill="{t["ink"]}" transform="translate(64 272)">{name}</g>
<g fill="{t["muted"]}" transform="translate(70 328)">{tag}</g>
</svg>
"""


def footer(t):
    W, H = 1280, 120
    line, _ = DISPLAY.path("FOLLOW ME ON X  @BADATVIM", 44, 2)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Follow me on X: @badAtVim">
<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{t["paint"]}"/>
  {flag_stripes(t, 1120, H, (16, 4, 16, 4, 16), 52)}
</g>
<g fill="{t["ink"]}" transform="translate(64 76)">{line}</g>
</svg>
"""


OUT.mkdir(exist_ok=True)
for old in ("hero.svg", "footer.svg"):
    (OUT / old).unlink(missing_ok=True)
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t))
    (OUT / f"footer-{mode}.svg").write_text(footer(t))
print("wrote", sorted(p.name for p in OUT.iterdir()))
