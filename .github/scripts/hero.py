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


TEXT_SEMI = Face("BricolageGrotesque.ttf", wght=600, wdth=100, opsz=18)

FEATURED = ("TumaBoda", "Same-day boda-boda delivery across Kenya. Riders get an app, customers follow their parcel on a live map, and shops book deliveries from their own checkout.", "Bun, Elysia, PostGIS, Go, Expo, Next.js")

PROJECTS = [
    ("Tessera", "A desktop SSH client that keeps your hosts, keys and snippets in a git repo you own. Secrets are encrypted per person before they're committed, so no company holds your credentials.", "TypeScript, Electron, React"),
    ("Linky", "Links your phones and computers. Share the clipboard and files, mirror notifications, control media, or ring a lost phone, over the local network or through a relay.", "Kotlin Multiplatform, Compose, Ktor"),
    ("Convo-Hub", "A platform for running business conversations on WhatsApp, with its own web app and a self-hosted deploy stack.", "Kotlin, TypeScript, Docker"),
    ("Multi-store commerce", "One Medusa backend running six storefronts, from fragrance to coffee to a restaurant menu, each with its own theme and checkout. Plus a desktop point of sale.", "Astro, Medusa, TypeScript"),
    ("Rent and tax", "Rent, leases and M-Pesa collection for landlords, and a gateway that files invoices with KRA eTIMS, retrying the ones that fail.", "Hono, Drizzle, PostgreSQL, Go"),
    ("On-device AI", "Small local models that turn what you say into actions in a mobile app, without sending your words to a server.", "React Native, Expo"),
]

STACK = [
    ("Mobile", "React Native and Expo, Kotlin and Compose Multiplatform, Android in Java, a little Swift when iOS demands it."),
    ("Web", "Next.js, Astro, React with TanStack, Svelte, Angular, Tailwind."),
    ("Backend", "Hono and Drizzle, Ktor, Spring Boot, Go, Medusa."),
    ("Data", "PostgreSQL, SQLite, MongoDB, MySQL, Redis, Neo4j, Supabase."),
    ("Shipping", "Docker, Traefik, GitHub Actions, Vercel, fastlane."),
]


def wrap(face, text, size, width):
    """Greedy line-wrap using the face's real advance widths."""
    space = face.path(" ", size)[1]
    lines, line, line_w = [], [], 0.0
    for word in text.split():
        w = face.path(word, size)[1]
        if line and line_w + space + w > width:
            lines.append(" ".join(line))
            line, line_w = [word], w
        else:
            line_w += (space if line else 0) + w
            line.append(word)
    return lines + [" ".join(line)]


def flag_rule(t, x, y):
    """A short black, red, green rule under a section title."""
    return "".join(f'<rect x="{x + i * 46}" y="{y}" width="40" height="6" fill="{c}"/>'
                   for i, c in enumerate([t["black"] if t["paint"] != "#16181C" else t["white"], t["red"], t["green"]]))


def section(t, title, body, height):
    W = 1280
    name, _ = DISPLAY.path(title, 64, 2)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img">
<rect width="{W}" height="{height}" rx="22" fill="{t["paint"]}"/>
<g fill="{t["ink"]}" transform="translate(64 108)">{name}</g>
{flag_rule(t, 66, 132)}
{body}
</svg>
"""


def projects(t):
    col_w, gap, size, lh = 548, 56, 23, 33
    rows, y, body = [PROJECTS[i:i + 2] for i in range(0, len(PROJECTS), 2)], 200, []
    # Featured project spans the full width, with a larger name.
    name, desc, stack_line = FEATURED
    title, title_w = DISPLAY.path(name.upper(), 64, 2)
    body.append(f'<g fill="{t["ink"]}" transform="translate(64 {y + 56})">{title}</g>')
    url, _ = TEXT_SEMI.path("tumaboda.co.ke", 22)
    body.append(f'<g fill="{t["green"]}" transform="translate({64 + title_w + 24} {y + 54})">{url}</g>')
    lines = wrap(TEXT, desc, 25, 1280 - 128)
    for i, line in enumerate(lines):
        p, _ = TEXT.path(line, 25)
        body.append(f'<g fill="{t["ink"]}" opacity=".86" transform="translate(64 {y + 102 + i * 36})">{p}</g>')
    sy = y + 102 + len(lines) * 36 + 10
    sp, _ = TEXT_SEMI.path(stack_line, 20)
    body.append(f'<g fill="{t["muted"]}" transform="translate(64 {sy})">{sp}</g>')
    y = sy + 54
    body.append(f'<rect x="64" y="{y - 20}" width="{1280 - 128}" height="1.5" fill="{t["muted"]}" opacity=".35"/>')
    for r, row in enumerate(rows):
        heights = []
        for c, (name, desc, stack) in enumerate(row):
            x = 64 + c * (col_w + gap)
            title, _ = DISPLAY.path(name.upper(), 40, 1.5)
            parts = [f'<g fill="{t["ink"]}" transform="translate({x} {y + 36})">{title}</g>']
            lines = wrap(TEXT, desc, size, col_w)
            for i, line in enumerate(lines):
                p, _ = TEXT.path(line, size)
                parts.append(f'<g fill="{t["ink"]}" opacity=".86" transform="translate({x} {y + 80 + i * lh})">{p}</g>')
            sy = y + 80 + len(lines) * lh + 10
            sp, _ = TEXT_SEMI.path(stack, 20)
            parts.append(f'<g fill="{t["muted"]}" transform="translate({x} {sy})">{sp}</g>')
            body.append("".join(parts))
            heights.append(sy - y + 20)
        y += max(heights) + 34
        if r < len(rows) - 1:
            body.append(f'<rect x="64" y="{y - 20}" width="{1280 - 128}" height="1.5" fill="{t["muted"]}" opacity=".35"/>')
    return section(t, "WHAT I'M BUILDING", "".join(body), y + 30)


def stack(t):
    y, body, label_w, size, lh = 200, [], 200, 24, 34
    for label, items in STACK:
        lp, _ = DISPLAY.path(label.upper(), 32, 1.5)
        body.append(f'<g fill="{t["ink"]}" transform="translate(64 {y + 26})">{lp}</g>')
        lines = wrap(TEXT, items, size, 1280 - 128 - label_w)
        for i, line in enumerate(lines):
            p, _ = TEXT.path(line, size)
            body.append(f'<g fill="{t["ink"]}" opacity=".86" transform="translate({64 + label_w} {y + 25 + i * lh})">{p}</g>')
        y += 25 + len(lines) * lh + 24
    note, _ = TEXT_SEMI.path("Next: OCaml and Haskell, on the way to writing my own compiler.", 22)
    body.append(f'<rect x="64" y="{y + 4}" width="{1280 - 128}" height="1.5" fill="{t["muted"]}" opacity=".35"/>')
    body.append(f'<g fill="{t["muted"]}" transform="translate(64 {y + 50})">{note}</g>')
    return section(t, "WHAT I REACH FOR", "".join(body), y + 86)


def numbers_header(t):
    return section(t, "THE NUMBERS", "", 168)


OUT.mkdir(exist_ok=True)
for old in ("hero.svg", "footer.svg"):
    (OUT / old).unlink(missing_ok=True)
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t))
    (OUT / f"footer-{mode}.svg").write_text(footer(t))
    (OUT / f"projects-{mode}.svg").write_text(projects(t))
    (OUT / f"stack-{mode}.svg").write_text(stack(t))
    (OUT / f"numbers-{mode}.svg").write_text(numbers_header(t))
print("wrote", sorted(p.name for p in OUT.iterdir()))
