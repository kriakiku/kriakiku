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


def tape_roll(outer=.92, inner=.5, core=.6, width=.82, sides=16):
    lines = []
    half = width / 2

    def circle(radius, z, role):
        return ([(radius * math.sin(2 * math.pi * k / sides), radius * math.cos(2 * math.pi * k / sides), z) for k in range(sides)], True, role, True)

    for z in (-half, half):
        lines += [circle(outer, z, "tape"), circle(core, z, "core"), circle(inner, z, "core"), circle(.76, z, "layer")]
    for k in range(0, sides, sides // 4):
        a = 2 * math.pi * k / sides + .25
        lines.append(([(outer * math.sin(a), outer * math.cos(a), -half), (outer * math.sin(a), outer * math.cos(a), half)], False, "tape", True))
        lines.append(([(inner * math.sin(a), inner * math.cos(a), -half), (inner * math.sin(a), inner * math.cos(a), half)], False, "core", True))
    x = outer
    for z in (-half, half):
        lines.append(([(x, 0, z), (x + .02, .55, z), (x - .01, 1.2, z)], False, "tape", False))
    teeth = [(x - .01 + (.035 if i % 2 else 0), 1.2 + (.07 if i % 2 else 0), -half + width * i / 8) for i in range(9)]
    lines.append((teeth, False, "tape", False))
    return lines


TAPE = tape_roll()
TAPE_COLORS = {"dark": {"tape": "#c9d1d9", "layer": "#8b949e", "core": "#d4a373"}, "light": {"tape": "#57606a", "layer": "#8c959f", "core": "#a87444"}}
SPIN, FRAMES = 30, 50


def solid(cx, cy, size, palette):
    scale = size / 2
    frames = []
    for f in range(FRAMES + 1):
        a = 2 * math.pi * f / FRAMES
        yaw = math.radians(28 + 38 * math.sin(a))
        tilt = math.radians(12 + 6 * math.sin(2 * a + .6))
        spin = math.radians(18 * math.sin(a + .9))
        bob = 2.5 * math.sin(2 * a)
        shapes = []
        for points, _, _, spins in TAPE:
            out = []
            for x, y, z in points:
                if spins:
                    x, y = x * math.cos(spin) - y * math.sin(spin), x * math.sin(spin) + y * math.cos(spin)
                x, z = x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw)
                y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
                k = scale / (1 - z * .12)
                out.append((cx + x * k, cy + bob + y * k, z))
            shapes.append(out)
        frames.append(shapes)
    times = ";".join(f"{f / FRAMES:.4f}" for f in range(FRAMES + 1))

    def d(points, closed):
        return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y, _ in points) + ("Z" if closed else "")

    paths = []
    for n, (_, closed, role, _) in enumerate(TAPE):
        shapes = ";".join(d(fr[n], closed) for fr in frames)
        depth = ";".join(f"{.3 + .6 * (1 + max(-1, min(1, sum(z for _, _, z in fr[n]) / len(fr[n]) * 1.6))) / 2:.2f}" for fr in frames)
        paths.append(
            f'<path d="{d(frames[0][n], closed)}" fill="none" stroke="{palette[role]}" stroke-width="{1.4 if role != "layer" else .8}" stroke-linejoin="round" stroke-linecap="round">'
            f'<animate attributeName="d" values="{shapes}" keyTimes="{times}" dur="{SPIN}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-opacity" values="{depth}" keyTimes="{times}" dur="{SPIN}s" repeatCount="indefinite"/></path>'
        )
    return "".join(paths)


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
{solid(784, 76, 76, TAPE_COLORS[t["name"]])}
</svg>'''


LAB_ACCENT = {"dark": "#7aa2ff", "light": "#3156c8"}
LAB_GLOWS = [(160, 120, 420, 240, "#3b82f6", .9), (640, 330, 380, 160, "#8b5cf6", .45), (840, 30, 260, 160, "#22d3ee", .4)]
LAB_PARTS = [
    ("UniFi Dream Router 7", "router, Wi-Fi 7", 120),
    ("UniFi Flex 2.5G Mini", "2.5G switch", 142),
    ("Tenda 8× 2.5G + 2× 10G SFP+", "core switch, 10G uplink", 164),
    ("3× HP EliteDesk G4 Mini", "compute nodes, 2.5G + 1G", 270),
    ("AOOSTAR WTR PRO", "NAS, Ryzen 7 5825U, 5G LAG", 316),
]


def led(x, y, color, period, delay=0, r=1.6):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"><animate attributeName="opacity" values="1;.25;1;1" keyTimes="0;.2;.35;1" '
            f'dur="{period}s" begin="{delay}s" repeatCount="indefinite"/></circle>')


def cable(x1, y1, x2, y2, sag, color, period=0, delay=0):
    return (f'<path d="M{x1} {y1}C{x1} {y1 + sag:.1f} {x2} {y2 - abs(y2 - y1) * .35:.1f} {x2} {y2}" fill="none" stroke="{color}" '
            f'stroke-width="2.2" stroke-linecap="round" opacity=".92"/>')


def homelab(t):
    h = 372
    name = t["name"]
    accent = LAB_ACCENT[name]
    text, meta = tones(accent, t)
    shape = squircle(1, 1, W - 2, h - 2, R)
    glows = "".join(
        f'<radialGradient id="g{i}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({x} {y}) scale({rx} {ry})">'
        f'<stop stop-color="{c}" stop-opacity="{t["glow"] * k:.2f}"/><stop offset=".55" stop-color="{c}" stop-opacity="{t["glow"] * k * .35:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, rx, ry, c, k) in enumerate(LAB_GLOWS)
    )
    layers = "".join(f'<rect x="-200" y="-100" width="{W + 400}" height="{h + 200}" fill="url(#g{i})"/>' for i in range(len(LAB_GLOWS)))
    dark = name == "dark"
    frame, inner, rail, hole = ("#2a2e35", "#121418", "#3a3f47", "#0b0c0e") if dark else ("#3a3f47", "#1c1f24", "#4a5059", "#101215")
    green, blue = "#4ade80", "#60a5fa"
    x0, x1, top, bottom = 48, 470, 52, 352
    parts = [f'''<defs><linearGradient id="pill" x1="0" x2="1"><stop stop-color="#cfd4d9"/><stop offset=".45" stop-color="#ffffff"/><stop offset="1" stop-color="#c4c9ce"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#3a3f46"/><stop offset="1" stop-color="#1f2226"/></linearGradient>
<linearGradient id="gun" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#4b5058"/><stop offset="1" stop-color="#2a2d32"/></linearGradient>
<linearGradient id="silver" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#f3f4f6"/><stop offset=".5" stop-color="#d1d5db"/><stop offset="1" stop-color="#e5e7eb"/></linearGradient>
<pattern id="perf" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".8" fill="#14161a"/></pattern></defs>''']
    parts.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" rx="10" fill="{frame}"/>')
    parts.append(f'<rect x="{x0 + 10}" y="{top + 10}" width="{x1 - x0 - 20}" height="{bottom - top - 20}" rx="4" fill="{inner}"/>')
    for rx_ in (x0 + 10, x1 - 22):
        parts.append(f'<rect x="{rx_}" y="{top + 10}" width="12" height="{bottom - top - 20}" fill="{rail}"/>')
        parts.append("".join(f'<rect x="{rx_ + 4}" y="{y}" width="4" height="4" rx=".8" fill="{hole}"/>' for y in range(top + 16, bottom - 14, 11)))
    ix0, ix1 = x0 + 26, x1 - 26

    shelf = 178
    parts.append(f'<rect x="{ix0}" y="{shelf}" width="{ix1 - ix0}" height="4" fill="{rail}"/>')
    rear = []
    ux, uw, uh = 90, 62, 104
    uy = shelf - uh
    cap = 15
    rear.append(f'<path d="M{ux} {uy + cap + 2}V{shelf - 22}a22 22 0 0 0 22 22h{uw - 44}a22 22 0 0 0 22 -22V{uy + cap + 2}Z" fill="url(#pill)"/>')
    rear.append(f'<path d="M{ux + 1} {uy + cap}C{ux + 2} {uy + 2} {ux + uw - 2} {uy + 2} {ux + uw - 1} {uy + cap}Z" fill="url(#pill)"/>')
    rear.append(f'<rect x="{ux}" y="{uy + cap}" width="{uw}" height="2.4" rx="1.2" fill="#3b9bff"><animate attributeName="opacity" values=".55;1;.55" dur="4s" repeatCount="indefinite"/></rect>')
    rear.append(f'<rect x="{ux - 2}" y="{uy + cap - 1.5}" width="{uw + 4}" height="5.4" rx="2.7" fill="#3b9bff" opacity=".18"/>')
    rear.append(f'<rect x="{ux + uw / 2 - 4.5}" y="{uy + 52}" width="9" height="20" rx="4.5" fill="#0f2a6b"/><rect x="{ux + uw / 2 - 3}" y="{uy + 56}" width="6" height="1.4" rx=".7" fill="#e0f2fe"/>'
                 f'<rect x="{ux + uw / 2 - 3}" y="{uy + 59.5}" width="4" height="1.2" rx=".6" fill="#7dd3fc"/><path d="M{ux + uw / 2 - 4.5} {uy + 67}q4.5 -3 9 0v1.5a4.5 4.5 0 0 1 -9 0Z" fill="#2563eb"/>')
    rear.append(f'<rect x="{ux + 10}" y="{shelf - 2.5}" width="{uw - 20}" height="2.5" rx="1.2" fill="#000" opacity=".25"/>')

    tx, tw, th = 160, 158, 34
    ty = shelf - th
    parts.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="2" fill="url(#metal)"/><rect x="{tx}" y="{ty}" width="{tw}" height="1" fill="#5a616a"/>')
    parts.append(f'<text x="{tx + 4}" y="{ty + 11}" font-family="{FONT}" font-size="6" font-style="italic" font-weight="800" fill="#e5e7eb">Tenda</text>'
                 f'<rect x="{tx + 6}" y="{ty + 13}" width="5" height="9" rx="1" fill="#0d0f12"/><rect x="{tx + 6.8}" y="{ty + 18}" width="3.4" height="3" rx=".6" fill="#6b7280"/>' + led(tx + 16, ty + 19, "#4ade80", 9, 0, .9))
    ports = [tx + 21 + i * 11.6 + (3 if i >= 4 else 0) for i in range(8)]
    for g in (ports[:4], ports[4:]):
        parts.append(f'<rect x="{g[0] - 1:.1f}" y="{ty + 11}" width="{g[-1] - g[0] + 12:.1f}" height="12" rx="1" fill="#9ca3af"/>')
    parts.append("".join(f'<rect x="{x:.1f}" y="{ty + 13}" width="10" height="10" rx=".6" fill="#0d0f12"/><rect x="{x + 2.5:.1f}" y="{ty + 21}" width="5" height="1" fill="#6b7280"/>' for x in ports))
    blink = [(.8 + (i * .29) % 1.3, i * .13, 1.3 + (i * .41) % 1.1, i * .21) for i in range(8)]
    blink[7] = blink[6]
    parts.append("".join(led(x + 1.8, ty + 14.3, "#4ade80", blink[i][0], blink[i][1], .6) + led(x + 8.2, ty + 14.3, "#fb923c" if i % 3 == 0 and i < 6 else "#4ade80", blink[i][2], blink[i][3], .6) for i, x in enumerate(ports)))
    parts.append("".join(f'<text x="{x + 5:.1f}" y="{ty + 29.5}" text-anchor="middle" font-family="{FONT}" font-size="3.6" fill="#d1d5db">{i + 1}</text>' for i, x in enumerate(ports)))
    sfp = [tx + 122 + i * 15 for i in range(2)]
    parts.append(f'<rect x="{sfp[0] - 1}" y="{ty + 6}" width="30" height="3.4" rx=".5" fill="#f3f4f6"/>')
    parts.append(f'<rect x="{sfp[0] - 1}" y="{ty + 12}" width="30" height="11" rx=".6" fill="#9ca3af"/>')
    parts.append("".join(f'<rect x="{x}" y="{ty + 13}" width="13" height="9" rx=".5" fill="#0d0f12"/>' for x in sfp))
    parts.append("".join(led(x + 6, ty + 26.5, "#4ade80", 1.7 + i * .6, i * .4, .6) for i, x in enumerate(sfp)))

    parts.append(f'<rect x="{ix0}" y="192" width="{ix1 - ix0}" height="16" rx="2" fill="#1a1d22" stroke="#3b4048"/>')
    parts.append(f'<rect x="{ix0 + 14}" y="198" width="{ix1 - ix0 - 28}" height="4" rx="2" fill="#0b0c0e"/>')

    floor = 330
    parts.append(f'<rect x="{ix0}" y="{floor}" width="{ix1 - ix0}" height="4" fill="{rail}"/>')
    ex, ew, eh = 80, 112, 22
    minis = []
    for n in range(3):
        y = floor - eh - n * (eh + 2)
        minis.append(y)
        top_h = eh * .5
        rear.append(f'<rect x="{ex}" y="{y}" width="{ew}" height="{eh}" rx="3" fill="#1b1d21"/>')
        rear.append(f'<clipPath id="vent{n}"><rect x="{ex + 3}" y="{y + 2}" width="{ew - 6}" height="{top_h - 3}" rx="2"/></clipPath>')
        rear.append(f'<g clip-path="url(#vent{n})">' + "".join(f'<path d="M{ex + 3 + k * 3.6:.1f} {y + top_h}l5 {-top_h}" stroke="#050607" stroke-width="1.6"/>' for k in range(-2, 32)) + "</g>")
        rear.append(f'<path d="M{ex} {y + top_h}H{ex + ew}V{y + eh - 3}a3 3 0 0 1 -3 3H{ex + 3}a3 3 0 0 1 -3 -3Z" fill="url(#silver)"/>')
        cy_ = y + top_h + (eh - top_h) / 2
        rear.append(f'<circle cx="{ex + 7}" cy="{cy_:.1f}" r="3" fill="none" stroke="#8a9098" stroke-width=".7"/><text x="{ex + 7}" y="{cy_ + 1.5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="3.6" font-style="italic" font-weight="700" fill="#8a9098">hp</text>')
        rear.append(f'<text x="{ex + 13}" y="{cy_ + 1.4:.1f}" font-family="{FONT}" font-size="3.4" letter-spacing=".6" fill="#4b5563">ELITEDESK</text>')
        rear.append(f'<rect x="{ex + 38}" y="{cy_ - .9:.1f}" width="5" height="1.8" rx=".9" fill="#1f2328"/><rect x="{ex + 47}" y="{cy_ - 1.4:.1f}" width="7" height="2.8" rx=".3" fill="#1f2328"/><rect x="{ex + 57}" y="{cy_ - 1.4:.1f}" width="7" height="2.8" rx=".3" fill="#1f2328"/>'
                     f'<circle cx="{ex + 69}" cy="{cy_:.1f}" r="1.2" fill="#1f2328"/><circle cx="{ex + 75}" cy="{cy_:.1f}" r="1.2" fill="#1f2328"/>')
        rear.append(led(ex + 82, cy_, "#f8fafc", 2.6 + n * .7, n * .5, .6))
        rear.append(f'<rect x="{ex + ew - 18}" y="{cy_ - 2.4:.1f}" width="13" height="4.8" rx="1" fill="none" stroke="#6b7280" stroke-width=".6"/><circle cx="{ex + ew - 11.5}" cy="{cy_:.1f}" r=".9" fill="none" stroke="#38bdf8" stroke-width=".4"/>')
    fx, fw, fh = tx + 8, 64, 12
    fy = ty - fh
    parts.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="2.5" fill="url(#pill)"/>')
    flex = [fx + 8 + i * 9 for i in range(5)]
    parts.append("".join(f'<rect x="{x}" y="{fy + 4}" width="6.5" height="5" rx=".8" fill="#2b2f36"/>' for x in flex))
    parts.append("".join(led(x + 3.25, fy + 2.2, green, 1.1 + i * .37, i * .2, .7) for i, x in enumerate(flex)))
    parts.append(f'<circle cx="{fx + fw - 6}" cy="{fy + 6}" r="1.2" fill="{blue}"/>')

    nw, nh = 100, 118
    nx, ny = 236, floor - nh
    rear.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="7" fill="url(#gun)"/><rect x="{nx + 6}" y="{ny + 6}" width="{nw - 12}" height="{nh - 12}" rx="3" fill="#0f1113"/>')
    for b in range(4):
        by = ny + 10 + b * 20
        rear.append(f'<rect x="{nx + 10}" y="{by}" width="{nw - 20}" height="18" rx="1.5" fill="#16181b" stroke="#2c3036" stroke-width=".6"/>')
        rear.append(f'<rect x="{nx + 14}" y="{by + 3}" width="10" height="12" rx="1" fill="#0a0b0d" stroke="#2c3036" stroke-width=".5"/>')
        rear.append("".join(f'<rect x="{nx + 28 + k * 7}" y="{by + 4}" width="4" height="10" rx=".6" fill="#050607"/>' for k in range(5)))
        rear.append(led(nx + 12.5, by + 6, "#4ade80", .6 + b * .23, b * .17, .8) + led(nx + 12.5, by + 12, "#60a5fa", 1.3 + b * .31, b * .29, .8))
    rear.append(f'<rect x="{nx + 10}" y="{ny + 92}" width="{nw - 20}" height="16" rx="1" fill="url(#perf)"/>')
    rear.append(f'<rect x="{nx + nw - 30}" y="{ny + 100}" width="20" height="7" rx="1" fill="#dc2626"/><text x="{nx + nw - 20}" y="{ny + 105.2}" text-anchor="middle" font-family="{FONT}" font-size="3.8" font-weight="800" fill="#fff">WTR PRO</text>')
    ny_top = ny

    fast, slow, lag, uplink = "#3b82f6", "#facc15", "#22c55e", "#e5e7eb"
    stack_top = minis[2]
    for n in range(3):
        for k, color in enumerate((fast, slow)):
            port = ports[n * 2 + k]
            drop = ex + ew / 2 - 14 + (n * 2 + k) * 5.6
            parts.append(cable(port + 5, ty + 22, drop, stack_top + 6, 18 + (n * 2 + k) * 4, color, 4.2 + n * .5 + k * .3, -(n * 2 + k) * .35))
    parts.append(cable(ports[6] + 5, ty + 22, nx + nw - 26, ny + 24, 26, lag, 4.4, -.3))
    parts.append(cable(ports[7] + 5, ty + 22, nx + nw - 16, ny + 24, 32, lag, 4.9, -.9))
    up = f"M{sfp[0] + 6} {ty + 21}C{sfp[0] + 6} {shelf + 34} {ux + uw + 8} {shelf + 30} {ux + uw + 6} {shelf - 6}S{ux + uw - 10} {shelf - 20} {ux + uw - 16} {shelf - 22}"
    parts.append(f'<path d="{up}" fill="none" stroke="{uplink}" stroke-width="2.2" stroke-linecap="round" opacity=".92"/>')
    flex_link = f"M{flex[0] + 3.25} {fy + 9}C{flex[0] + 3.25} {fy + 16} {ux + uw + 10} {fy + 15} {ux + uw - 12} {fy + 13}"
    parts.append(f'<path d="{flex_link}" fill="none" stroke="#f472b6" stroke-width="2.2" stroke-linecap="round" opacity=".92"/>')
    parts.extend(rear)

    rows = []
    for i, (title, role, _) in enumerate(LAB_PARTS):
        y = (top + bottom) / 2 - (len(LAB_PARTS) - 1) * 13 + i * 26 + 5
        rows.append(f'<circle cx="{x1 + 18}" cy="{y - 4}" r="2.5" fill="{accent}"/>')
        rows.append(f'<text x="{x1 + 30}" y="{y}" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["title"]}">{title}<tspan font-weight="400" font-size="13" fill="{meta}" dx="8">{role}</tspan></text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h - top + 2}" viewBox="0 {top - 2} {W} {h - top + 2}">
{"".join(parts)}{"".join(rows)}
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
        write(f"homelab-{theme}", homelab(colors))
        for p in PROJECTS:
            write(f"plaque-{p['slug']}-{theme}", plaque(p, colors))
