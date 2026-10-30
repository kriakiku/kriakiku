#!/usr/bin/env python3
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

GREEN = "#3ddc84"
ORANGE = "#ff7a1a"
AMBER = "#ffb547"
FUCHSIA = "#d946ef"
FUCHSIA_SOFT = "#f0abfc"

HOLTDROID = (
    '<g fill="none"><path d="M8 40c0-13.3 10.7-24 24-24s24 10.7 24 24v8H8z" fill="#8a5a3c"/>'
    '<circle cx="23" cy="32" r="3.5" fill="#1b1b1b"/><circle cx="41" cy="32" r="3.5" fill="#1b1b1b"/>'
    f'<path d="M20 16l-4-7M44 16l4-7" stroke="{GREEN}" stroke-width="4" stroke-linecap="round"/>'
    '<ellipse cx="32" cy="39" rx="5" ry="3.5" fill="#d9b48f"/><circle cx="32" cy="38" r="1.8" fill="#1b1b1b"/>'
    f'<rect x="4" y="48" width="56" height="8" rx="4" fill="{GREEN}"/></g>'
)
HOLTKEEPER = (
    '<g fill="none"><circle cx="13.5" cy="25.5" r="4.6" fill="#d95a0b"/><circle cx="50.5" cy="25.5" r="4.6" fill="#d95a0b"/>'
    f'<circle cx="13.5" cy="25.5" r="2" fill="{AMBER}"/><circle cx="50.5" cy="25.5" r="2" fill="{AMBER}"/>'
    f'<path d="M8 42c0-14 10.7-25 24-25s24 11 24 25v6H8z" fill="{ORANGE}"/>'
    '<circle cx="23" cy="32" r="3.4" fill="#1a120c"/><circle cx="24.2" cy="30.8" r="1.1" fill="#fff"/>'
    '<circle cx="41" cy="32" r="3.4" fill="#1a120c"/><circle cx="42.2" cy="30.8" r="1.1" fill="#fff"/>'
    '<ellipse cx="32" cy="41.5" rx="12" ry="6.5" fill="#ffe6cc"/>'
    '<path d="M21 39.5l-8.5-1.8M21 42.5l-8.5 1M43 39.5l8.5-1.8M43 42.5l8.5 1" stroke="#ffe6cc" stroke-opacity=".85" stroke-width="1.2" stroke-linecap="round"/>'
    '<ellipse cx="32" cy="38.2" rx="3.3" ry="2.3" fill="#1a120c"/>'
    '<path d="M28.6 41.6q1.7 2 3.4 0q1.7 2 3.4 0" stroke="#1a120c" stroke-width="1.4" stroke-linecap="round"/>'
    f'<circle cx="11" cy="52.5" r="5" stroke="{AMBER}" stroke-width="3.4"/>'
    f'<rect x="15.5" y="50.8" width="42.5" height="3.4" rx="1.7" fill="{AMBER}"/>'
    f'<rect x="45" y="52" width="3.4" height="6.5" rx="1.2" fill="{AMBER}"/>'
    f'<rect x="51" y="52" width="3.4" height="4.8" rx="1.2" fill="{AMBER}"/></g>'
)

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Menlo, SF Mono, monospace"

PROJECTS = [
    {
        "name": "holtdroid",
        "title": "Holtdroid",
        "icon": HOLTDROID,
        "accent": GREEN,
        "tagline": "A cozy holt for your test Androids.",
        "lines": ["Self-hosted Android sandboxes for APK", "testing: device screen, WebView DevTools,", "clipboard and VPN in one browser tab."],
        "chips": ["Go", "React", "Kotlin", "Kubernetes"],
    },
    {
        "name": "holtkeeper",
        "title": "Holtkeeper",
        "icon": HOLTKEEPER,
        "accent": ORANGE,
        "tagline": "The keeper of your repository holt.",
        "lines": ["An automation engine for a fleet of Git", "repositories: AI review, dependency updates,", "audits and releases on GitLab and GitHub."],
        "chips": ["TypeScript", "Bun", "GitLab", "GitHub"],
    },
]

STACK = [
    ("TypeScript", "#3178c6"),
    ("Go", "#00add8"),
    ("Swift", "#f05138"),
    ("Kotlin", "#a97bff"),
    ("Python", "#3572a5"),
    ("React", "#61dafb"),
    ("Bun", "#fbf0df"),
    ("Nix", "#7e7eff"),
    ("Nushell", "#4e9a06"),
    ("Kubernetes", "#326ce5"),
    ("Home Assistant", "#18bcf2"),
    ("Claude Code", "#d97757"),
]


def background(w, h, glows, strip=None):
    stops = "".join(
        f'<radialGradient id="glow{i}" cx="{x}" cy="{y}" r="{r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{c}" stop-opacity=".2"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, r, c) in enumerate(glows)
    )
    layers = "".join(f'<rect width="{w}" height="{h}" fill="url(#glow{i})"/>' for i in range(len(glows)))
    bar = ""
    if strip:
        bar = (
            f'<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{strip[0]}"/><stop offset="1" stop-color="{strip[-1]}"/></linearGradient>'
        )
    return f"""<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="24"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0f0d12"/><stop offset="1" stop-color="#18121b"/>
  </linearGradient>
  <pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.4" fill="#fff" fill-opacity=".05"/>
  </pattern>
  {stops}{bar}
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect width="{w}" height="{h}" fill="url(#dots)"/>
{layers}
{f'<rect y="{h - 10}" width="{w}" height="10" fill="url(#bar)"/>' if strip else ""}
</g>"""


def banner():
    w, h = 1280, 420
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{background(w, h, [(260, 220, 420, FUCHSIA), (900, 230, 260, GREEN), (1140, 230, 260, ORANGE)], [FUCHSIA, FUCHSIA_SOFT])}
<text x="80" y="128" font-family="{MONO}" font-size="28" fill="#9b92a3"><tspan fill="{FUCHSIA}">~/</tspan>kriakiku</text>
<text x="76" y="218" font-family="{FONT}" font-size="88" font-weight="700" fill="#faf7fc">Jonas D.</text>
<text x="80" y="274" font-family="{FONT}" font-size="34" fill="#cdc5d4">Web developer from Vilnius, Lithuania.</text>
<text x="80" y="318" font-family="{FONT}" font-size="24" fill="#958c9e">Simplifying the world around me by overengineering it :D</text>
<g transform="translate(770 120) scale(3.6)">{HOLTDROID}</g>
<g transform="translate(1010 120) scale(3.6)">{HOLTKEEPER}</g>
<text x="885" y="370" text-anchor="middle" font-family="{MONO}" font-size="20" fill="#7d8f86">holtdroid</text>
<text x="1125" y="370" text-anchor="middle" font-family="{MONO}" font-size="20" fill="#a08670">holtkeeper</text>
</svg>"""


def chips(x, y, items, accent, size=28):
    out, cx = [], x
    for c in items:
        width = 36 + len(c) * size * 0.62
        out.append(
            f'<rect x="{cx}" y="{y}" width="{width}" height="{size * 2}" rx="{size}" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".5" stroke-width="1.5"/>'
            f'<text x="{cx + width / 2}" y="{y + size * 1.36}" text-anchor="middle" font-family="{FONT}" font-size="{size}" font-weight="500" fill="#f1ebf5">{c}</text>'
        )
        cx += width + 14
    return "".join(out)


def card(p):
    w, h = 1200, 640
    lines = "".join(
        f'<text x="64" y="{370 + i * 54}" font-family="{FONT}" font-size="40" fill="#c8c0cf">{l}</text>' for i, l in enumerate(p["lines"])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{background(w, h, [(170, 150, 420, p["accent"])], [p["accent"], p["accent"]])}
<g transform="translate(48 30) scale(3.4)">{p["icon"]}</g>
<text x="306" y="118" font-family="{MONO}" font-size="30" fill="{p["accent"]}">{p["name"]}/<tspan fill="#9b92a3">{p["name"]}</tspan></text>
<text x="302" y="206" font-family="{FONT}" font-size="88" font-weight="700" fill="#faf7fc">{p["title"]}</text>
<text x="306" y="258" font-family="{FONT}" font-size="34" fill="{p["accent"]}" fill-opacity=".9">{p["tagline"]}</text>
{lines}
{chips(64, 524, p["chips"], p["accent"])}
</svg>"""


def stack():
    w, size, gap = 1280, 24, 14
    rows, row, x = [], [], 0
    for name, color in STACK:
        width = 64 + len(name) * size * 0.58
        if x + width > w and row:
            rows.append(row)
            row, x = [], 0
        row.append((name, color, width))
        x += width + gap
    rows.append(row)
    h = len(rows) * 70 - 14
    out = []
    for r, items in enumerate(rows):
        total = sum(i[2] for i in items) + gap * (len(items) - 1)
        cx = (w - total) / 2
        y = r * 70
        for name, color, width in items:
            out.append(
                f'<rect x="{cx}" y="{y}" width="{width}" height="56" rx="28" fill="#17121b" stroke="{color}" stroke-opacity=".55" stroke-width="1.5"/>'
                f'<circle cx="{cx + 30}" cy="{y + 28}" r="8" fill="{color}"/>'
                f'<text x="{cx + 48}" y="{y + 36}" font-family="{FONT}" font-size="{size}" font-weight="500" fill="#efeaf3">{name}</text>'
            )
            cx += width + gap
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(out)}</svg>'


def write(name, svg, width):
    path = OUT / f"{name}.svg"
    path.write_text(svg)
    subprocess.run(["rsvg-convert", "-w", str(width), "-o", str(OUT / f"{name}.png"), str(path)], check=True)


OUT.mkdir(parents=True, exist_ok=True)
write("banner", banner(), 1280)
write("stack", stack(), 1280)
for p in PROJECTS:
    write(f"card-{p['name']}", card(p), 1200)
