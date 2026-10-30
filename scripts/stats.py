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
ORANGE = "#ff7a1a"
AMBER = "#ffb547"
GREEN = "#3ddc84"

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


def streaks(days):
    counts = [d["contributionCount"] for d in days]
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


def collect(data):
    user = data["user"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]
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
    months = collections.OrderedDict()
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
    current, longest = streaks(days)
    return {
        "total": calendar["totalContributions"],
        "current": current,
        "longest": longest,
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": repo_count,
        "languages": [(n, s, colors[n]) for n, s in languages.most_common(6)],
        "months": list(months.items())[-12:],
    }


def tile(x, y, value, label, accent):
    return (
        f'<rect x="{x}" y="{y}" width="278" height="112" rx="18" fill="#fff" fill-opacity=".035" stroke="#fff" stroke-opacity=".07"/>'
        f'<text x="{x + 24}" y="{y + 62}" font-family="{FONT}" font-size="46" font-weight="700" fill="{accent}">{value}</text>'
        f'<text x="{x + 24}" y="{y + 92}" font-family="{FONT}" font-size="19" fill="#a8988a">{label}</text>'
    )


def render(s):
    w, h = 1280, 520
    tiles = "".join(
        tile(40 + i * 302, 84, v, l, a)
        for i, (v, l, a) in enumerate(
            [
                (f"{s['total']:,}", "contributions, last year", ORANGE),
                (f"{s['current']}d", "current streak", AMBER),
                (f"{s['longest']}d", "longest streak", AMBER),
                (f"{s['stars']}★ · {s['repos']}", "stars · public repos", GREEN),
            ]
        )
    )

    peak = max((c for _, c in s["months"]), default=0) or 1
    bars = []
    for i, (month, count) in enumerate(s["months"]):
        bh = max(4, 150 * count / peak)
        x = 40 + i * 56
        name = datetime.date(int(month[:4]), int(month[5:]), 1).strftime("%b")
        bars.append(
            f'<rect x="{x}" y="{430 - bh}" width="40" height="{bh}" rx="8" fill="url(#bar)"/>'
            f'<text x="{x + 20}" y="458" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#8a7b6e">{name}</text>'
            f'<text x="{x + 20}" y="{422 - bh}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#c9bcb0">{count}</text>'
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
            f'<text x="{cx + 26}" y="{cy}" font-family="{FONT}" font-size="21" fill="#e6dcd2">{name}</text>'
            f'<text x="{cx + 230}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="18" fill="#8a7b6e">{100 * size / total:.1f}%</text>'
        )

    updated = datetime.date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="24"/></clipPath>
  <clipPath id="langs"><rect x="740" y="250" width="500" height="22" rx="11"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f0e0c"/><stop offset="1" stop-color="#18130f"/></linearGradient>
  <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
  <radialGradient id="glow" cx="300" cy="420" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".16"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="#fff" fill-opacity=".05"/></pattern>
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#dots)"/><rect width="{w}" height="{h}" fill="url(#glow)"/>
</g>
<text x="40" y="54" font-family="{MONO}" font-size="22" fill="{ORANGE}">~/kriakiku <tspan fill="#9c8d80">· stats</tspan></text>
<text x="1240" y="54" text-anchor="end" font-family="{MONO}" font-size="18" fill="#6f6359">updated {updated}</text>
{tiles}
<text x="40" y="250" font-family="{FONT}" font-size="20" font-weight="600" fill="#e6dcd2">Contributions by month</text>
{"".join(bars)}
<text x="740" y="230" font-family="{FONT}" font-size="20" font-weight="600" fill="#e6dcd2">Languages</text>
<g clip-path="url(#langs)">{"".join(segments)}</g>
{"".join(legend)}
</svg>"""


out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist/stats.svg")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(render(collect(fetch())))
