#!/usr/bin/env python3
import datetime
import math
import pathlib
import re
import sys
import zoneinfo

GREEN = "#3ddc84"
ORANGE = "#ff7a1a"
FUCHSIA = "#d946ef"
FUCHSIA_SOFT = "#f0abfc"

HOLTDROID = (
    '<g fill="none"><path d="M8 40c0-13.3 10.7-24 24-24s24 10.7 24 24v8H8z" fill="#8a5a3c"/>'
    '<circle cx="23" cy="32" r="3.5" fill="#1b1b1b"/><circle cx="41" cy="32" r="3.5" fill="#1b1b1b"/>'
    f'<path d="M20 16l-4-7M44 16l4-7" stroke="{GREEN}" stroke-width="4" stroke-linecap="round"/>'
    '<ellipse cx="32" cy="39" rx="5" ry="3.5" fill="#d9b48f"/><circle cx="32" cy="38" r="1.8" fill="#1b1b1b"/>'
    f'<rect x="4" y="48" width="56" height="8" rx="4" fill="{GREEN}"/></g>'
)
HOLTKEEPER = '<g fill="none"><circle cx="12.5" cy="16.5" r="8" fill="#76593f"/><circle cx="12.5" cy="16.5" r="3.8" fill="#eadccb" fill-opacity=".55"/><circle cx="51.5" cy="16.5" r="8" fill="#76593f"/><circle cx="51.5" cy="16.5" r="3.8" fill="#eadccb" fill-opacity=".55"/><path d="M32 9C47 9 57 19 58 32C58.5 37 60 41 62.5 44C59.5 44.5 58 45.5 57.5 47C60 48.5 61 50 61 51.5C57 51 55 52 52.5 54C47 58.5 40 60 32 60C24 60 17 58.5 11.5 54C9 52 7 51 3 51.5C3 50 4 48.5 6.5 47C6 45.5 4.5 44.5 1.5 44C4 41 5.5 37 6 32C7 19 17 9 32 9Z" fill="#9c7a5e"/><ellipse cx="32" cy="50" rx="15" ry="8.5" fill="#eadccb"/><path d="M9 33.5c4-6.5 12.5-7.5 17.5-3.5 3 2.4 8 2.4 11 0 5-4 13.5-3 17.5 3.5-4.5 4-12 4.5-17 1.8-3.2-1.7-8.8-1.7-12 0-5 2.7-12.5 2.2-17-1.8z" fill="#0b0b0c" fill-opacity=".34"/><circle cx="21.5" cy="32" r="3.2" fill="#0b0b0c"/><circle cx="22.55" cy="30.95" r="1.05" fill="#fff"/><circle cx="42.5" cy="32" r="3.2" fill="#0b0b0c"/><circle cx="43.55" cy="30.95" r="1.05" fill="#fff"/><ellipse cx="32" cy="45.2" rx="3.4" ry="2.3" fill="#0b0b0c"/></g>'

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Menlo, SF Mono, monospace"
W, H, R = 880, 132, 44


def squircle(x, y, w, h, r, n=5, steps=12):
    def corner(cx, cy, a0):
        pts = []
        for i in range(steps + 1):
            t = math.radians(a0 + 90 * i / steps)
            c, s = math.cos(t), math.sin(t)
            pts.append((cx + r * math.copysign(abs(c) ** (2 / n), c), cy + r * math.copysign(abs(s) ** (2 / n), s)))
        return pts
    pts = corner(x + w - r, y + r, 270) + corner(x + w - r, y + h - r, 0) + corner(x + r, y + h - r, 90) + corner(x + r, y + r, 180)
    return "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + "Z"


def eventide(t):
    day = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Vilnius"))
    return (
        '<linearGradient id="ring" gradientUnits="userSpaceOnUse" x1="4" y1="32" x2="60" y2="32">'
        '<stop stop-color="#7f77dd"/><stop offset=".5" stop-color="#4c4499"/><stop offset="1" stop-color="#7f77dd"/>'
        '<animateTransform attributeName="gradientTransform" type="rotate" from="0 32 32" to="360 32 32" dur="30s" repeatCount="indefinite"/>'
        '</linearGradient>'
        f'<path d="{squircle(9, 4, 46, 56, 12)}" fill="{t["ev_tile"]}" stroke="url(#ring)" stroke-width="1.75"/>'
        f'<text x="32" y="21" text-anchor="middle" font-family="{FONT}" font-size="12.5" fill="{t["ev_t2"]}">{day:%a}</text>'
        f'<line x1="10" x2="54" y1="27" y2="27" stroke="{t["ev_rule"]}" stroke-width="1"/>'
        f'<text x="32" y="51" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="600" fill="{t["ev_t1"]}">{day.day}</text>'
    )


def holtkeeper_eyes(icon):
    eyes = re.findall(r'<circle cx="(?:2[12]|4[23])[.\d]*" cy="3[0-2][.\d]*" r="[\d.]+" fill="#(?:0b0b0c|fff)"/>', icon)
    for e in eyes:
        icon = icon.replace(e, "")
    return icon + '<g class="eye">' + "".join(eyes) + "</g>"



PROJECTS = [
    dict(slug="holtdroid", url="https://github.com/holtdroid", repo="holtdroid/holtdroid", title="Holtdroid", accent=GREEN,
         glows=[(60, 40, 300, 150, GREEN, 1), (430, 150, 320, 110, "#14b8a6", .7), (800, -10, 200, 110, "#a3e635", .45)],
         text="Self-hosted Android sandboxes in a browser tab for APK and WebView testing.",
         icon=HOLTDROID.replace('<path d="M20 16l-4-7M44 16l4-7"', '<path class="ant" d="M20 16l-4-7M44 16l4-7"'),
         css=".ant{transform-origin:32px 17px;animation:wiggle 4s ease-in-out infinite}"
             "@keyframes wiggle{0%,80%,100%{transform:rotate(0)}85%{transform:rotate(-8deg)}90%{transform:rotate(7deg)}95%{transform:rotate(-4deg)}}"),
    dict(slug="holtkeeper", url="https://github.com/holtkeeper", repo="holtkeeper/holtkeeper", title="Holtkeeper", accent=ORANGE,
         glows=[(70, 110, 300, 150, ORANGE, 1), (470, -20, 300, 110, "#ffb547", .65), (830, 140, 220, 120, "#f43f5e", .5)],
         text="AI review, dependency updates, audits and releases for a fleet of Git repositories.",
         icon=holtkeeper_eyes(HOLTKEEPER),
         css=".eye{transform-origin:32px 32px;animation:blink 5s infinite}"
             "@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}"),
    dict(slug="favicons", url="https://favicons.page", repo="peleda-app/favicons", title="favicons.page", accent="#e8613c",
         glows=[(40, 70, 280, 160, "#e8613c", 1), (380, -30, 300, 100, "#fbbf24", .55), (790, 150, 260, 120, FUCHSIA, .55)],
         text="Any website’s icon as a clean, sandboxed SVG with light and dark theme colours.",
         icon=lambda t: f'<g transform="translate(32 32) scale(1.15) translate(-32 -34)"><path d="M8 52V24a8 8 0 0 1 8-8h20a8 8 0 0 1 7.2 4.5L48 30h0a4 4 0 0 0 3.6 2.2H56V52Z" fill="{t["fv_glyph"]}"/><rect class="dot" x="15" y="22" width="14" height="14" rx="4" fill="#e8613c"/><rect x="33" y="27" width="10" height="4" rx="2" fill="{t["fv_slot"]}" opacity=".25"/></g>',
         css=".dot{animation:hue 24s ease-in-out infinite}"
             "@keyframes hue{0%,100%{fill:#e8613c}25%{fill:#ffb547}50%{fill:#3ddc84}75%{fill:#7f77dd}}"),
    dict(slug="eventide", url="https://github.com/kriakiku/eventide-card", repo="kriakiku/eventide-card", title="Eventide", accent="#7f77dd",
         glows=[(80, 20, 300, 150, "#7f77dd", 1), (420, 160, 300, 110, "#e0704a", .6), (820, 0, 220, 120, "#4f46e5", .6)],
         text="A Home Assistant calendar card where events rise before they start and ebb while they run.",
         icon=eventide,
         css=""),
]

THEMES = {
    "dark": dict(name="dark", fv_glyph="#fbf0df", fv_slot="#141416", bg="#16131a", bg2="#1f1a24", stroke="#2c2632", title="#faf7fc", text="#bdb4c6", meta="#8a8094", glow=.34,
                 ev_tile="#1c1b24", ev_t1="#f2f0f8", ev_t2="#aba8b8", ev_rule="#3c3a49"),
    "light": dict(name="light", fv_glyph="#e2cfae", fv_slot="#141416", bg="#ffffff", bg2="#f7f4f9", stroke="#e6e0ea", title="#1a1520", text="#4f4757", meta="#857c8e", glow=.2,
                 ev_tile="#ffffff", ev_t1="#1f1d2b", ev_t2="#6a6778", ev_rule="#e4e2ee"),
}


def wrap(text, width=58):
    lines, line = [], ""
    for w in text.split():
        if len(line) + len(w) + 1 > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return lines + [line]


def mix(a, b, k):
    ca, cb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return "#" + "".join(f"{round(x * k + y * (1 - k)):02x}" for x, y in zip(ca, cb))


TINT = {"dark": (("#ece8f0", .22), ("#9a93a2", .4)), "light": (("#3d3844", .25), ("#7a7382", .35))}


def tones(accent, t):
    (text, kt), (meta, km) = TINT[t["name"]]
    return mix(accent, text, kt), mix(accent, meta, km)


def plaque(p, t):
    icon = p["icon"](t) if callable(p["icon"]) else p["icon"]
    glows = "".join(
        f'<radialGradient id="g{i}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({x} {y}) scale({rx} {ry})">'
        f'<stop stop-color="{c}" stop-opacity="{t["glow"] * k:.2f}"/><stop offset=".55" stop-color="{c}" stop-opacity="{t["glow"] * k * .35:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, rx, ry, c, k) in enumerate(p["glows"])
    )
    layers = "".join(f'<rect class="d{i}" x="-200" y="-100" width="{W + 400}" height="{H + 200}" fill="url(#g{i})"/>' for i in range(len(p["glows"])))
    shape = squircle(1, 1, W - 2, H - 2, R)
    tile = squircle(20, 18, 96, 96, 30)
    a = p["accent"]
    text, meta = tones(a, t)
    body = "".join(f'<text x="148" y="{94 + i * 22}" font-family="{FONT}" font-size="17" fill="{text}">{l}</text>' for i, l in enumerate(wrap(p["text"])))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{p["css"]}
.d0{{animation:a0 11s ease-in-out infinite alternate}}.d1{{animation:a1 14s ease-in-out infinite alternate}}.d2{{animation:a2 9s ease-in-out infinite alternate}}
@keyframes a0{{to{{transform:translate(90px,10px)}}}}@keyframes a1{{to{{transform:translate(-120px,-14px)}}}}@keyframes a2{{to{{transform:translate(-60px,18px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<defs><clipPath id="c"><path d="{shape}"/></clipPath>
{glows}</defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>{layers}</g>
<path d="{shape}" fill="none" stroke="{t["stroke"]}" stroke-width="1.5"/>
<path d="{tile}" fill="{t["bg2"]}" stroke="{t["stroke"]}"/>
<svg x="32" y="30" width="72" height="72" viewBox="0 0 64 64">{icon}</svg>
<text x="148" y="40" font-family="{MONO}" font-size="14" fill="{meta}"><tspan fill="{a}">{p["repo"].split("/")[0]}/</tspan>{p["repo"].split("/")[1]}</text>
<text x="146" y="70" font-family="{FONT}" font-size="28" font-weight="700" fill="{t["title"]}">{p["title"]}</text>
{body}
<path d="M{W - 60} 58l10 8-10 8" fill="none" stroke="{meta}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


HERO_ACCENT = {"dark": "#38c8e6", "light": "#0e7490"}
HERO_GLOWS = [(120, 40, 420, 220, "#0ea5e9", 1), (520, 260, 420, 160, "#22d3ee", .7), (860, 30, 300, 180, "#2dd4bf", .55)]
HERO_ROLE = "Senior frontend / conceptual engineer"
HERO_LINES = [
    "Built my first WAP site at six, on a Siemens, under the blanket after bedtime.",
    "Still up past bedtime: by day I shake up iGaming, by night I vibe-code open source",
    "to scratch my own itches. Addicted to frontend optimization: lean delivery paths",
    "and apps that fly on potato phones. Simplifying the world by overengineering it.",
]


def hero(t):
    h = 276
    shape = squircle(1, 1, W - 2, h - 2, R)
    glows = "".join(
        f'<radialGradient id="g{i}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({x} {y}) scale({rx} {ry})">'
        f'<stop stop-color="{c}" stop-opacity="{t["glow"] * k:.2f}"/><stop offset=".55" stop-color="{c}" stop-opacity="{t["glow"] * k * .35:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, rx, ry, c, k) in enumerate(HERO_GLOWS)
    )
    layers = "".join(f'<rect class="d{i}" x="-200" y="-100" width="{W + 400}" height="{h + 200}" fill="url(#g{i})"/>' for i in range(len(HERO_GLOWS)))
    text, meta = tones(HERO_ACCENT[t["name"]], t)
    body = "".join(f'<text x="44" y="{166 + i * 24}" font-family="{FONT}" font-size="17" fill="{text}">{l}</text>' for i, l in enumerate(HERO_LINES))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>.d0{{animation:a0 13s ease-in-out infinite alternate}}.d1{{animation:a1 17s ease-in-out infinite alternate}}.d2{{animation:a2 11s ease-in-out infinite alternate}}
@keyframes a0{{to{{transform:translate(120px,16px)}}}}@keyframes a1{{to{{transform:translate(-140px,-20px)}}}}@keyframes a2{{to{{transform:translate(-80px,24px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<defs><clipPath id="c"><path d="{shape}"/></clipPath>{glows}</defs>
<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="{t["bg"]}"/>{layers}</g>
<path d="{shape}" fill="none" stroke="{t["stroke"]}" stroke-width="1.5"/>
<text x="46" y="56" font-family="{MONO}" font-size="16" fill="{meta}"><tspan fill="{HERO_ACCENT[t["name"]]}">~/</tspan>kriakiku</text>
<text x="44" y="134" font-family="{FONT}" font-size="18" font-weight="600" fill="{HERO_ACCENT[t["name"]]}">{HERO_ROLE}</text>
<text x="42" y="106" font-family="{FONT}" font-size="50" font-weight="700" fill="{t["title"]}">Jonas Danilá</text>
{body}
</svg>'''


def write(name, svg):
    (OUT / f"{name}.svg").write_text(svg)


def glow_layers(glows, t, h):
    defs = "".join(
        f'<radialGradient id="g{i}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({x} {y}) scale({rx} {ry})">'
        f'<stop stop-color="{c}" stop-opacity="{t["glow"] * k:.2f}"/><stop offset=".55" stop-color="{c}" stop-opacity="{t["glow"] * k * .35:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, rx, ry, c, k) in enumerate(glows)
    )
    layers = "".join(f'<rect class="d{i}" x="-200" y="-100" width="{W + 400}" height="{h + 200}" fill="url(#g{i})"/>' for i in range(len(glows)))
    return defs, layers


DRIFT = """.d0{animation:a0 13s ease-in-out infinite alternate}.d1{animation:a1 17s ease-in-out infinite alternate}.d2{animation:a2 11s ease-in-out infinite alternate}
@keyframes a0{to{transform:translate(120px,16px)}}@keyframes a1{to{transform:translate(-140px,-20px)}}@keyframes a2{to{transform:translate(-80px,24px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}"""


if __name__ == "__main__":
    OUT = pathlib.Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, colors in THEMES.items():
        write(f"hero-{theme}", hero(colors))
        for p in PROJECTS:
            write(f"plaque-{p['slug']}-{theme}", plaque(p, colors))
