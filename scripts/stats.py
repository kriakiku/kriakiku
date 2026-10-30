#!/usr/bin/env python3
import collections
import datetime
import json
import os
import pathlib
import subprocess
import sys
import urllib.request

LOGIN = "kriakiku"
ORGS = ["holtdroid", "holtkeeper"]
SKIP_LANGUAGES = {"Dockerfile", "Makefile", "Shell", "HTML", "CSS", "Just", "Smarty"}

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Menlo, SF Mono, monospace"
ACCENT = "#d946ef"
ACCENT_SOFT = "#f0abfc"
GREEN = "#3ddc84"
CYAN = "#0891b2"
CYAN_SOFT = "#67e8f9"

REPOS = "nodes { isFork stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }"
QUERY = (
    "query { user(login: \"%s\") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } }"
    " repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount %s } }" % (LOGIN, REPOS)
    + "".join(f' {o.replace("-", "_")}: organization(login: "{o}") {{ repositories(first: 100, privacy: PUBLIC) {{ totalCount {REPOS} }} }}' for o in ORGS)
    + " }"
)


def token():
    return os.environ.get("GITHUB_TOKEN") or subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"},
    )
    body = json.load(urllib.request.urlopen(req))
    if body.get("errors"):
        sys.exit(json.dumps(body["errors"], indent=2))
    return body["data"]


def fetch_gitlab():
    with urllib.request.urlopen(f"https://gitlab.com/users/{LOGIN}/calendar.json") as res:
        return json.load(res)


def streaks(counts):
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def collect(data, gitlab):
    user = data["user"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    github = {d["date"]: d["contributionCount"] for w in calendar["weeks"] for d in w["contributionDays"]}
    repos = [r for r in user["repositories"]["nodes"] if not r["isFork"]]
    repo_count = user["repositories"]["totalCount"]
    for o in ORGS:
        org = data[o.replace("-", "_")]["repositories"]
        repos += [r for r in org["nodes"] if not r["isFork"]]
        repo_count += org["totalCount"]
    languages, colors = collections.Counter(), {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in SKIP_LANGUAGES:
                languages[name] += e["size"]
                colors[name] = e["node"]["color"] or "#888"
    first = datetime.date.fromisoformat(min(github))
    last = datetime.date.fromisoformat(max(github))
    dates = [(first + datetime.timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]
    months = collections.OrderedDict()
    for d in dates:
        hub, lab = months.get(d[:7], (0, 0))
        months[d[:7]] = (hub + github.get(d, 0), lab + gitlab.get(d, 0))
    current, longest = streaks([github.get(d, 0) + gitlab.get(d, 0) for d in dates])
    return {
        "github": sum(github.values()),
        "gitlab": sum(gitlab.get(d, 0) for d in dates),
        "current": current,
        "longest": longest,
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": repo_count,
        "languages": [(n, s, colors[n]) for n, s in languages.most_common(6)],
        "months": list(months.items())[-12:],
        "weeks": [[d["date"] for d in w["contributionDays"]] for w in calendar["weeks"]],
        "days": {d: github.get(d, 0) + gitlab.get(d, 0) for d in dates},
    }


def tile(x, y, value, label, accent):
    return (
        f'<rect x="{x}" y="{y}" width="278" height="112" rx="18" fill="#fff" fill-opacity=".035" stroke="#fff" stroke-opacity=".07"/>'
        f'<text x="{x + 24}" y="{y + 62}" font-family="{FONT}" font-size="46" font-weight="700" fill="{accent}">{value}</text>'
        f'<text x="{x + 24}" y="{y + 92}" font-family="{FONT}" font-size="19" fill="#a39aab">{label}</text>'
    )


def render(s):
    w, h = 1280, 520
    tiles = "".join(
        tile(40 + i * 302, 84, v, l, a)
        for i, (v, l, a) in enumerate(
            [
                (f"{s['github'] + s['gitlab']:,}", "contributions, last year", ACCENT),
                (f"{s['current']}d", "current streak", ACCENT_SOFT),
                (f"{s['longest']}d", "longest streak", ACCENT_SOFT),
                (f"{s['stars']}★ · {s['repos']}", "stars · public repos", CYAN_SOFT),
            ]
        )
    )

    peak = max((hub + lab for _, (hub, lab) in s["months"]), default=0) or 1
    bars = []
    for i, (month, (hub, lab)) in enumerate(s["months"]):
        count = hub + lab
        bh = max(4, 150 * count / peak)
        lh = bh * lab / count if count else 0
        x = 40 + i * 56
        name = datetime.date(int(month[:4]), int(month[5:]), 1).strftime("%b")
        bars.append(
            f'<clipPath id="m{i}"><rect x="{x}" y="{430 - bh}" width="40" height="{bh}" rx="8"/></clipPath>'
            f'<g clip-path="url(#m{i})"><rect x="{x}" y="{430 - bh}" width="40" height="{bh}" fill="url(#bar)"/>'
            f'<rect x="{x}" y="{430 - lh}" width="40" height="{lh}" fill="url(#lab)"/></g>'
            f'<text x="{x + 20}" y="458" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#8a8193">{name}</text>'
            f'<text x="{x + 20}" y="{422 - bh}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#c8c0cf">{count}</text>'
        )

    total = sum(size for _, size, _ in s["languages"]) or 1
    lx, segments, legend = 740, [], []
    for i, (name, size, color) in enumerate(s["languages"]):
        width = 500 * size / total
        segments.append(f'<rect x="{lx}" y="250" width="{width}" height="22" fill="{color}"/>')
        lx += width
        cx, cy = 740 + (i % 2) * 250, 320 + (i // 2) * 44
        legend.append(
            f'<circle cx="{cx + 8}" cy="{cy - 6}" r="8" fill="{color}"/>'
            f'<text x="{cx + 26}" y="{cy}" font-family="{FONT}" font-size="21" fill="#e8e2ee">{name}</text>'
            f'<text x="{cx + 230}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="18" fill="#8a8193">{100 * size / total:.1f}%</text>'
        )

    updated = datetime.date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="24"/></clipPath>
  <clipPath id="langs"><rect x="740" y="250" width="500" height="22" rx="11"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f0d12"/><stop offset="1" stop-color="#18121b"/></linearGradient>
  <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT_SOFT}"/></linearGradient>
  <linearGradient id="lab" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN_SOFT}"/></linearGradient>
  <radialGradient id="glow" cx="300" cy="420" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".16"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="#fff" fill-opacity=".05"/></pattern>
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#dots)"/><rect width="{w}" height="{h}" fill="url(#glow)"/>
</g>
<text x="40" y="54" font-family="{MONO}" font-size="22" fill="{ACCENT}">~/kriakiku <tspan fill="#9b92a3">· stats</tspan></text>
<text x="1240" y="54" text-anchor="end" font-family="{MONO}" font-size="18" fill="#6d6575">updated {updated}</text>
{tiles}
<text x="40" y="250" font-family="{FONT}" font-size="20" font-weight="600" fill="#e8e2ee">Contributions by month</text>
<circle cx="388" cy="243" r="7" fill="{ACCENT}"/><text x="402" y="250" font-family="{FONT}" font-size="18" fill="#c8c0cf">GitHub <tspan fill="#8a8193">{s['github']:,}</tspan></text>
<circle cx="548" cy="243" r="7" fill="{CYAN_SOFT}"/><text x="562" y="250" font-family="{FONT}" font-size="18" fill="#c8c0cf">GitLab <tspan fill="#8a8193">{s['gitlab']:,}</tspan></text>
{"".join(bars)}
<text x="740" y="230" font-family="{FONT}" font-size="20" font-weight="600" fill="#e8e2ee">Languages</text>
<g clip-path="url(#langs)">{"".join(segments)}</g>
{"".join(legend)}
</svg>"""


HEAT = ["#1f1a24", "#4a1450", "#86198f", "#c026d3", ACCENT, ACCENT_SOFT]


def activity(s):
    w, h, step, cell, x0, y0 = 1280, 330, 21, 17, 100, 118
    active = sorted(c for c in s["days"].values() if c)
    cuts = [active[int(len(active) * q)] for q in (0.25, 0.5, 0.75, 0.9)] if active else []

    def level(c):
        return 0 if not c else 1 + sum(c > t for t in cuts)

    cells, months, seen = [], [], set()
    for i, week in enumerate(s["weeks"]):
        x = x0 + i * step
        month = week[0][:7]
        if month not in seen and int(week[0][8:]) <= 7:
            seen.add(month)
            name = datetime.date.fromisoformat(week[0]).strftime("%b")
            months.append(f'<text x="{x}" y="{y0 - 14}" font-family="{FONT}" font-size="16" fill="#8a8193">{name}</text>')
        for date in week:
            row = datetime.date.fromisoformat(date).isoweekday() % 7
            cells.append(
                f'<rect class="c" style="animation-delay:{i * 0.03:.2f}s" x="{x}" y="{y0 + row * step}" width="{cell}" height="{cell}" rx="4" fill="{HEAT[level(s["days"].get(date, 0))]}"/>'
            )
    labels = "".join(
        f'<text x="88" y="{y0 + r * step + 13}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#6d6575">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    gx = x0 + len(s["weeks"]) * step - 4
    scale = "".join(f'<rect x="{gx - (6 - i) * 21 - 36}" y="290" width="{cell}" height="{cell}" rx="4" fill="{c}"/>' for i, c in enumerate(HEAT))
    total = sum(s["days"].values())
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>
.c {{ animation: pop .5s ease-out both; transform-box: fill-box; transform-origin: center; }}
@keyframes pop {{ from {{ opacity: 0; transform: scale(.2); }} }}
.scan {{ animation: scan 7s 2s ease-in-out infinite; }}
@keyframes scan {{ from {{ transform: translateX(0); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} to {{ transform: translateX({gx - x0}px); opacity: 0; }} }}
</style>
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="24"/></clipPath>
  <clipPath id="grid"><rect x="{x0}" y="{y0}" width="{gx - x0}" height="{7 * step - 4}"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f0d12"/><stop offset="1" stop-color="#18121b"/></linearGradient>
  <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT_SOFT}" stop-opacity="0"/><stop offset=".5" stop-color="{ACCENT_SOFT}" stop-opacity=".22"/><stop offset="1" stop-color="{ACCENT_SOFT}" stop-opacity="0"/></linearGradient>
  <radialGradient id="glow" cx="{gx - 120}" cy="190" r="520" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".14"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#frame)"><rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#glow)"/></g>
<text x="40" y="54" font-family="{MONO}" font-size="22" fill="{ACCENT}">~/kriakiku <tspan fill="#9b92a3">· activity</tspan></text>
<text x="1240" y="54" text-anchor="end" font-family="{FONT}" font-size="18" fill="#c8c0cf">{total:,} contributions <tspan fill="#8a8193">· GitHub + GitLab</tspan></text>
{"".join(months)}{labels}
{"".join(cells)}
<g clip-path="url(#grid)"><rect class="scan" x="{x0 - 60}" y="{y0}" width="60" height="{7 * step - 4}" fill="url(#beam)"/></g>
<text x="{gx - 6 * 21 - 46}" y="304" text-anchor="end" font-family="{FONT}" font-size="15" fill="#8a8193">Less</text>
{scale}
<text x="{gx}" y="304" text-anchor="end" font-family="{FONT}" font-size="15" fill="#8a8193">More</text>
</svg>"""


out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
out.mkdir(parents=True, exist_ok=True)
stats = collect(fetch(), fetch_gitlab())
(out / "stats.svg").write_text(render(stats))
(out / "activity.svg").write_text(activity(stats))
active = sorted(c for c in stats["days"].values() if c)
cuts = [active[int(len(active) * q)] for q in (0.25, 0.5, 0.75)] if active else []
levels = {d: (1 + sum(c > t for t in cuts)) if c else 0 for d, c in stats["days"].items()}
(out / "levels.json").write_text(json.dumps(levels))
