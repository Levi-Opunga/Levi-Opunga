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

FEATURED = [("TumaBoda", "Same-day boda-boda delivery across Kenya. Riders get an app, customers follow their parcel on a live map, and shops book deliveries from their own checkout.", "Bun, Elysia, PostGIS, Go, Expo, Next.js", "tumaboda.co.ke"),
            ("TsavoSync", "Prepaid smart water meters for utilities. Customers top up with mobile money and get a meter token in seconds, issued through a hardware security module. The utility tracks readings, credit and tariffs from one dashboard.", "Kotlin, Spring Boot, GraphQL, Go, Next.js, Expo", None)]

PROJECTS = [
    ("Tessera", "A desktop SSH client that keeps your hosts, keys and snippets in a git repo you own. Secrets are encrypted per person before they're committed, so no company holds your credentials.", "TypeScript, Electron, React"),
    ("Linky", "Links your phones and computers. Share the clipboard and files, mirror notifications, control media, or ring a lost phone, over the local network or through a relay.", "Kotlin Multiplatform, Compose, Ktor"),
    ("Convo-Hub", "A platform for running business conversations on WhatsApp, with its own web app and a self-hosted deploy stack.", "Kotlin, TypeScript, Docker"),
    ("Multi-store commerce", "One Medusa backend running six storefronts, from fragrance to coffee to a restaurant menu, each with its own theme and checkout. Plus a desktop point of sale.", "Astro, Medusa, TypeScript"),
    ("Boma", "Property management for Kenyan landlords and managing agents: rent, leases, invoicing, M-Pesa collection, KRA tax filing and landlord payouts.", "Hono, Drizzle, PostgreSQL, React"),
    ("PesaFlow", "A budget tracker that fills itself in. It reads your M-Pesa and bank messages, files each transaction, and learns your categories. A small AI model on the phone answers questions about your money.", "React Native, Expo, SQLite, on-device AI"),
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


def slug(name):
    return "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-")


def corner_stripes(t, width, height):
    bands = [(t["black"], 12), (t["white"], 3), (t["red"], 12), (t["white"], 3), (t["green"], 12)]
    x, out = width - 70, []
    for color, w in bands:
        out.append(f'<polygon points="{x},{height} {x + w},{height} {x + w + 150},0 {x + 150},0" fill="{color}"/>')
        x += w
    return "".join(out)


def project_card(t, name, desc, stack_line, width, height, url=None, featured=False):
    """One project on its own painted card: name, description, stack."""
    pad, size, lh = 44, 24, 34
    title, title_w = DISPLAY.path(name.upper(), 52 if featured else 46, 1.5)
    parts = [f'<g fill="{t["ink"]}" transform="translate({pad} {pad + 44})">{title}</g>']
    if url:
        u, _ = TEXT_SEMI.path(url, 22)
        parts.append(f'<g fill="{t["green"]}" transform="translate({pad + title_w + 22} {pad + 42})">{u}</g>')
    for i, line in enumerate(wrap(TEXT, desc, size, width - pad * 2 - 40)):
        p, _ = TEXT.path(line, size)
        parts.append(f'<g fill="{t["ink"]}" opacity=".86" transform="translate({pad} {pad + 94 + i * lh})">{p}</g>')
    sp, _ = TEXT_SEMI.path(stack_line, 20)
    parts.append(f'<g fill="{t["muted"]}" transform="translate({pad} {height - pad + 6})">{sp}</g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{name}">
<clipPath id="c"><rect width="{width}" height="{height}" rx="18"/></clipPath>
<g clip-path="url(#c)">
  <rect width="{width}" height="{height}" fill="{t["paint"]}"/>
  {corner_stripes(t, width, height)}
</g>
{"".join(parts)}
</svg>
"""


def card_height(desc, width, size=24, lh=34, pad=44):
    lines = len(wrap(TEXT, desc, size, width - pad * 2 - 40))
    return pad + 94 + (lines - 1) * lh + 56 + pad


def project_cards(t):
    """Yield (filename, svg). Small cards share one height so pairs line up."""
    for feat_name, feat_desc, feat_stack, url in FEATURED:
        yield f"project-{slug(feat_name)}", project_card(t, feat_name, feat_desc, feat_stack, 1280, card_height(feat_desc, 1280), url, featured=True)
    h = max(card_height(d, 620) for _, d, _ in PROJECTS)
    for name, desc, stack_line in PROJECTS:
        yield f"project-{slug(name)}", project_card(t, name, desc, stack_line, 620, h)


def building_header(t):
    return section(t, "WHAT I'M BUILDING", "", 168)


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
for old in ("hero.svg", "footer.svg", "projects-light.svg", "projects-dark.svg"):
    (OUT / old).unlink(missing_ok=True)
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t))
    (OUT / f"footer-{mode}.svg").write_text(footer(t))
    (OUT / f"building-{mode}.svg").write_text(building_header(t))
    for name, svg in project_cards(t):
        (OUT / f"{name}-{mode}.svg").write_text(svg)
    (OUT / f"stack-{mode}.svg").write_text(stack(t))
    (OUT / f"numbers-{mode}.svg").write_text(numbers_header(t))
print("wrote", sorted(p.name for p in OUT.iterdir()))
