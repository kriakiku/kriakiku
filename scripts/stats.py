#!/usr/bin/env python3
import datetime
import json
import math
import os
import pathlib
import subprocess
import sys
import urllib.request

from render import FONT, MONO, R, THEMES, W, glow_layers, squircle

LOGIN = "kriakiku"
ORGS = ["holtdroid", "holtkeeper", "peleda-app", "holtmail", "archived-dreams"]

TRACK = {"dark": "#2fbf4a", "light": "#15803d"}
RED = {"dark": "#f43f5e", "light": "#e11d48"}
VALUE = {"dark": "#3fcf5a", "light": "#166534"}
LABEL = {"dark": "#9cc9a6", "light": "#4f7358"}
GLOWS = [(140, 60, 420, 220, "#16a34a", 1), (560, 300, 420, 180, "#15803d", .65), (860, 40, 300, 180, "#22c55e", .5)]

REPOS = "nodes { isFork stargazerCount }"
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
    first = datetime.date.fromisoformat(min(github))
    last = datetime.date.fromisoformat(max(github))
    dates = [(first + datetime.timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]
    current, longest = streaks([github.get(d, 0) + gitlab.get(d, 0) for d in dates])
    return {
        "github": sum(github.values()),
        "gitlab": sum(gitlab.get(d, 0) for d in dates),
        "current": current,
        "longest": longest,
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": repo_count,
        "dates": dates,
        "hub": [github.get(d, 0) for d in dates],
        "lab": [gitlab.get(d, 0) for d in dates],
        "days": {d: github.get(d, 0) + gitlab.get(d, 0) for d in dates},
    }


DEPTH = (4, -10)


def weekly(values, k=3):
    weights = [math.exp(-((j / k) ** 2) / 2) for j in range(-3 * k, 3 * k + 1)]
    out = []
    for i in range(len(values)):
        num = den = 0
        for j, w in zip(range(-3 * k, 3 * k + 1), weights):
            if 0 <= i + j < len(values):
                num += values[i + j] * w
                den += w
        out.append(num / den)
    picks = list(range(0, len(out), 12))
    if picks[-1] != len(out) - 1:
        picks.append(len(out) - 1)
    return [(i, out[i]) for i in picks]


def line(points):
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in points)


def rounded(points, radius=16):
    out = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for prev, here, nxt in zip(points, points[1:], points[2:]):
        a, b = math.dist(prev, here), math.dist(here, nxt)
        r = min(radius, a / 2, b / 2)
        p = (here[0] + (prev[0] - here[0]) * r / a, here[1] + (prev[1] - here[1]) * r / a)
        q = (here[0] + (nxt[0] - here[0]) * r / b, here[1] + (nxt[1] - here[1]) * r / b)
        out += f"L{p[0]:.1f} {p[1]:.1f}Q{here[0]:.1f} {here[1]:.1f} {q[0]:.1f} {q[1]:.1f}"
    return out + f"L{points[-1][0]:.1f} {points[-1][1]:.1f}"


def flag(x, y, track, fill, delay=0):
    return (
        f'<g transform="translate({x:.1f} {y:.1f})"><path d="M0 0V-24" stroke="{track}" stroke-width="1.4" stroke-linecap="round"/>'
        f'<g transform="translate(.7 -24)"><g><path d="M0 0L13 4.5L0 9Z" fill="{fill}"/>'
        f'<animateTransform attributeName="transform" type="skewY" values="0;-7;0;5;0" dur="2.4s" begin="{delay}s" repeatCount="indefinite"/></g></g>'
        f'<circle r="1.6" fill="{track}"/></g>'
    )


SCALE = 2
SPRITE_W, SPRITE_H, CELL = 26 * SCALE, 22 * SCALE, 1.6 / SCALE
WHEELS = [(5, 16), (21, 16)]
BIKE = [((5, 16), (11, 13), 0.6), ((9, 11), (17, 11), 1.0), ((21, 16), (19, 8), 0.6), ((18, 7), (20, 7), 0.5), ((2, 12), (8, 11), 0.6), ((19, 11), (24, 12), 0.6)]
LEGS = [((12, 14), (15, 11), 0.7), ((15, 11), (12, 8), 0.8)]
SUIT = [((12, 8), (14, 4), 1.0), ((14, 4), (17, 5), 0.5), ((17, 5), (19, 7), 0.5)]


def pixels():
    cells = {}

    def put(x, y, color):
        if 0 <= x < SPRITE_W and 0 <= y < SPRITE_H:
            cells[(x, y)] = color

    def stroke(a, b, r, color):
        a, b, r = (a[0] * SCALE, a[1] * SCALE), (b[0] * SCALE, b[1] * SCALE), r * SCALE
        n = max(1, int(math.dist(a, b) * 4))
        for i in range(n + 1):
            px, py = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
            for x in range(int(px - r) - 1, int(px + r) + 2):
                for y in range(int(py - r) - 1, int(py + r) + 2):
                    if math.dist((x, y), (px, py)) <= r:
                        put(x, y, color)

    for cx, cy in WHEELS:
        cx, cy = cx * SCALE, cy * SCALE
        for x in range(SPRITE_W):
            for y in range(SPRITE_H):
                d = math.dist((x, y), (cx, cy)) / SCALE
                if 3.6 <= d <= 4.7:
                    put(x, y, "tyre")
                elif d < 0.8:
                    put(x, y, "hub")
    for a, b, r in BIKE:
        stroke(a, b, r, "bike")
    for x in range(10 * SCALE, 15 * SCALE):
        for y in range(13 * SCALE, 16 * SCALE):
            put(x, y, "engine")
    for a, b, r in LEGS:
        stroke(a, b, r, "pants")
    for a, b, r in SUIT:
        stroke(a, b, r, "suit")
    stroke((11, 14), (13, 14), 0.6, "boot")
    for x in range(SPRITE_W):
        for y in range(SPRITE_H):
            d = math.dist((x, y), (15 * SCALE, 1.8 * SCALE)) / SCALE
            if d <= 2.4:
                put(x, y, "visor" if x >= 15.8 * SCALE and 0.9 * SCALE <= y <= 2.4 * SCALE else "helmet")
    outline = {}
    for x in range(-1, SPRITE_W + 1):
        for y in range(-1, SPRITE_H + 1):
            if (x, y) not in cells and any((x + dx, y + dy) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                outline[(x, y)] = "line"
    return {**outline, **cells}


def spokes(frame):
    cells = set()
    for cx, cy in WHEELS:
        dirs = ((1, 0), (0, 1)) if frame == 0 else ((1, 1), (1, -1))
        reach = 6 if frame == 0 else 4
        for dx, dy in dirs:
            for k in range(-reach, reach + 1):
                if abs(k) > 1:
                    cells.add((cx * SCALE + dx * k, cy * SCALE + dy * k))
    return cells


def rects(cells, colors):
    runs = {}
    for (x, y), name in sorted(cells.items(), key=lambda c: (c[0][1], c[0][0])):
        if cells.get((x - 1, y)) == name:
            continue
        run = 1
        while cells.get((x + run, y)) == name:
            run += 1
        runs.setdefault(colors[name], []).append(f"M{x * CELL:.2f} {y * CELL:.2f}h{run * CELL + .05:.2f}v{CELL + .05:.2f}h{-(run * CELL + .05):.2f}z")
    return "".join(f'<path fill="{color}" d="{"".join(parts)}"/>' for color, parts in runs.items())


def rider(ink, bike, accent):
    colors = {"tyre": "#26262b", "hub": "#c9c9cf", "bike": bike, "engine": "#8a8a93", "suit": ink, "pants": "#3b4252", "boot": "#1f2937",
              "helmet": accent, "visor": "#1d2b3a", "line": "#0b0b0e"}
    frames = "".join(
        f'<g fill="#9a9aa3" opacity="{1 - f}">{rects(dict.fromkeys(spokes(f), "spoke"), {"spoke": "#9a9aa3"})}'
        f'<animate attributeName="opacity" values="{1 - f};{f}" dur=".24s" calcMode="discrete" repeatCount="indefinite"/></g>'
        for f in (0, 1)
    )
    return f'<g transform="translate({-SPRITE_W * CELL / 2:.2f} {-21 * SCALE * CELL:.2f})">{rects(pixels(), colors)}{frames}</g>'


RIDE, INTRO, OUTRO = 30, 2.2, 2.2
DUR = RIDE + INTRO + OUTRO
HEIGHT = 300


def stage(t):
    return (INTRO + t * RIDE) / DUR
LEVEL_OPACITY = (.035, .07, .12, .18, .26)


def grid(s, x0, x1, top, edge, color):
    days = [a + b for a, b in zip(s["hub"], s["lab"])]
    active = sorted(c for c in days if c)
    cuts = [active[int(len(active) * q)] for q in (.25, .5, .75)] if active else []

    def floor(x):
        for (ax, ay), (bx, by) in zip(edge, edge[1:]):
            if ax <= x <= bx:
                return ay + (by - ay) * (x - ax) / (bx - ax)
        return edge[0][1] if x < edge[0][0] else edge[-1][1]

    def slots(pitch):
        out = []
        columns = int((x1 - x0) // pitch)
        for col in range(columns):
            x = x0 + col * pitch
            limit = min(floor(x), floor(x + pitch * .72))
            y = top
            while y + pitch * .36 < limit:
                out.append((x, y))
                y += pitch
        return out

    pitch = 16.0
    while len(slots(pitch)) < len(days):
        pitch -= .1
    places = slots(pitch)
    size = pitch * .72
    r = size * .28
    side = size - 2 * r
    levels = [[] for _ in LEVEL_OPACITY]
    owner = {round(i * len(places) / len(days)): i for i in range(len(days))}
    for i, (x, y) in enumerate(places):
        c = days[owner[i]] if i in owner else 0
        level = 0 if not c else 1 + sum(c > t for t in cuts)
        levels[level].append(
            f"M{x + r:.1f} {y:.1f}h{side:.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f}v{side:.1f}a{r:.1f} {r:.1f} 0 0 1 {-r:.1f} {r:.1f}"
            f"h{-side:.1f}a{r:.1f} {r:.1f} 0 0 1 {-r:.1f} {-r:.1f}v{-side:.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f}z"
        )
    return "".join(f'<path fill="{color}" fill-opacity="{o}" d="{"".join(p)}"/>' for o, p in zip(LEVEL_OPACITY, levels) if p), [places[round(i * len(places) / len(days))] for i in range(len(days))], size


TRAIL, GLOW = 8, .01


def trail(places, moments, size, color):
    rects = []
    for k in range(TRAIL):
        opacity, xs, ys = [(0.0, 0.0)], [(0.0, places[k][0])], [(0.0, places[k][1])]
        for i in range(k, len(places), TRAIL):
            t = moments[i]
            nxt = moments[i + TRAIL] if i + TRAIL < len(moments) else 1.0
            length = min(1.0 / DUR, (nxt - t) * .95)
            if t <= opacity[-1][0] or length <= 0:
                continue
            opacity += [(t, 0.0), (t + length * .3, GLOW), (t + length, 0.0)]
            xs.append((t, places[i][0]))
            ys.append((t, places[i][1]))
        opacity.append((1.0, 0.0))
        xs.append((1.0, xs[-1][1]))
        ys.append((1.0, ys[-1][1]))

        def anim(attr, keys, mode="linear"):
            keys = sorted(dict(keys).items())
            return (f'<animate attributeName="{attr}" values="{";".join(f"{v:.2f}" if attr == "opacity" else f"{v:.1f}" for _, v in keys)}" '
                    f'keyTimes="{";".join(f"{t:.4f}" for t, _ in keys)}" calcMode="{mode}" dur="{DUR}s" repeatCount="indefinite"/>')

        rects.append(
            f'<rect x="{places[k][0]:.1f}" y="{places[k][1]:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size * .28:.1f}" fill="{color}" opacity="0">'
            f'{anim("opacity", opacity)}{anim("x", xs, "discrete")}{anim("y", ys, "discrete")}</rect>'
        )
    return "".join(rects)


def timeline(front):
    lengths = [0]
    for a, b in zip(front, front[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    total = lengths[-1]

    def at(x):
        for (a, b), l in zip(zip(front, front[1:]), lengths):
            if a[0] <= x <= b[0]:
                return (l + math.dist(a, b) * (x - a[0]) / (b[0] - a[0])) / total
        return 1.0

    return at, [l / total for l in lengths]


TRICK_SPAN = {"flip": .036, "wheelie": .034, "hop": .016}
TRICK_SLOW = 1.15
UP, DOWN, EVEN = ".2 .7 .4 1", ".6 0 .8 .3", "0 0 1 1"


def tricks(s, at, x_of, front):
    days = [a + b for a, b in zip(s["hub"], s["lab"])]
    weeks = sorted(((sum(days[i:i + 7]), i + 3) for i in range(0, len(days) - 6, 7)), reverse=True)
    chosen = []
    for total, day in weeks:
        f = at(x_of(day))
        if total and .06 < f < .94 and all(abs(f - g) > .09 for g, _ in chosen):
            kind = "flip" if len(chosen) < 3 else "wheelie" if len(chosen) < 7 else "hop"
            chosen.append((f, kind))
        if len(chosen) == 12:
            break
    chosen.sort()

    edges = [0.0]
    for f, kind in chosen:
        edges += [f - TRICK_SPAN[kind], f + TRICK_SPAN[kind]]
    edges.append(1.0)
    weights = [(b - a) * (TRICK_SLOW if i % 2 else 1) for i, (a, b) in enumerate(zip(edges, edges[1:]))]
    total = sum(weights)
    times = [0.0]
    for w in weights:
        times.append(times[-1] + w / total)

    def clock(p):
        for (a, b), (ta, tb) in zip(zip(edges, edges[1:]), zip(times, times[1:])):
            if a <= p <= b:
                return ta + (tb - ta) * ((p - a) / (b - a) if b > a else 0)
        return 1.0

    lift, turn, angle = [(0, "0 0", EVEN)], [(0, "0 0 -16", EVEN)], 0
    for f, kind in chosen:
        hw = TRICK_SPAN[kind]
        if kind == "flip":
            lift += [(f - hw, "0 0", EVEN), (f, "0 -38", UP), (f + hw, "0 0", DOWN)]
            turn += [(f - hw * .8, f"{angle} 0 -16", EVEN), (f + hw * .8, f"{angle - 360} 0 -16", ".4 0 .6 1")]
            angle -= 360
        elif kind == "wheelie":
            turn += [(f - hw, f"{angle} -13 0", EVEN), (f - hw / 2, f"{angle - 26} -13 0", UP), (f + hw / 2, f"{angle - 26} -13 0", EVEN), (f + hw, f"{angle} -13 0", DOWN)]
        else:
            lift += [(f - hw, "0 0", EVEN), (f, "0 -14", UP), (f + hw, "0 0", DOWN)]
    lift.append((1, "0 0", EVEN))
    turn.append((1, f"{angle} 0 -16", EVEN))

    def anim(kind, keys):
        keys = [(0, keys[0][1], EVEN, 0.0)] + [(k, v, sp, stage(clock(k))) for k, v, sp in keys] + [(1, keys[-1][1], EVEN, 1.0)]
        key_times = ";".join(f"{t:.4f}" for _, _, _, t in keys)
        values = ";".join(v for _, v, _, _ in keys)
        splines = ";".join(sp for _, _, sp, _ in keys[1:])
        return f'<animateTransform attributeName="transform" type="{kind}" values="{values}" keyTimes="{key_times}" calcMode="spline" keySplines="{splines}" dur="{DUR}s" repeatCount="indefinite"/>'

    lengths = [0]
    for a, b in zip(front, front[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    full = lengths[-1]

    def point(p):
        d = min(max(p, 0), 1) * full
        for (a, b), l0, l1 in zip(zip(front, front[1:]), lengths, lengths[1:]):
            if d <= l1:
                k = (d - l0) / (l1 - l0) if l1 > l0 else 0
                return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        return front[-1]

    def slope(p):
        span = 14 / full
        (ax, ay), (bx, by) = point(p - span), point(p + span)
        return math.degrees(math.atan2(by - ay, bx - ax))

    air = [(f - TRICK_SPAN[k], f + TRICK_SPAN[k]) for f, k in chosen if k != "wheelie"]

    def place(p):
        for a, b in air:
            if a < p < b:
                (ax, ay), (bx, by) = point(a), point(b)
                k = (p - a) / (b - a)
                return ax + (bx - ax) * k, ay + (by - ay) * k, None
        return (*point(p), slope(p))

    def progress(t):
        for (a, b), (ta, tb) in zip(zip(edges, edges[1:]), zip(times, times[1:])):
            if ta <= t <= tb:
                return a + (b - a) * ((t - ta) / (tb - ta) if tb > ta else 0)
        return 1.0

    steps = [i / 480 for i in range(481)]
    spots = [place(progress(t)) for t in steps]
    for i, (x, y, angle) in enumerate(spots):
        if angle is None:
            j = i
            while spots[j][2] is None:
                j -= 1
            k = i
            while spots[k][2] is None:
                k += 1
            w = (i - j) / (k - j)
            spots[i] = (x, y, spots[j][2] + (spots[k][2] - spots[j][2]) * w)
    hold = 16

    def around(cx, cy, angle):
        r = math.radians(angle)
        return cx - hold * math.sin(r), cy + hold * math.cos(r)

    def centre(x, y, angle):
        r = math.radians(angle)
        return x + hold * math.sin(r), y - hold * math.cos(r)

    sx, sy, sa = spots[0]
    fx, fy, fa = spots[-1]
    scx, scy = centre(sx, sy, sa)
    fcx, fcy = centre(fx, fy, fa)
    intro = []
    for i in range(40):
        u = i / 40
        cx = -40 + (scx + 40) * u
        cy = (scy - 22) + 22 * u - 4 * 30 * u * (1 - u)
        angle = sa - 360 * (1 - u)
        intro.append((u * INTRO / DUR, *around(cx, cy, angle), angle))
    outro = []
    for i in range(1, 41):
        u = i / 40
        cx = fcx + 70 * u * OUTRO
        cy = fcy - 60 * u + 520 * u * u
        angle = fa + 420 * u
        outro.append(((INTRO + RIDE + u * OUTRO) / DUR, *around(cx, cy, angle), angle))
    track = intro + [(stage(t), x, y, a) for t, (x, y, a) in zip(steps, spots)] + outro
    key_times = ";".join(f"{t:.4f}" for t, _, _, _ in track)
    spots = [(x, y, a) for _, x, y, a in track]
    motion = f'values="{";".join(f"{x:.1f},{y:.1f}" for x, y, _ in spots)}" keyTimes="{key_times}" calcMode="linear"'
    tilt = f'<animateTransform attributeName="transform" type="rotate" values="{";".join(f"{a:.1f}" for _, _, a in spots)}" keyTimes="{key_times}" dur="{DUR}s" repeatCount="indefinite"/>'
    return anim("translate", lift), anim("rotate", turn), clock, motion, tilt


def render(s, t):
    h, base, top, x0, x1 = 300, 262, 124, 32, W - 52
    name = t["name"]
    shape = squircle(1, 1, W - 2, h - 2, R)
    defs, layers = glow_layers(GLOWS, t, h)
    n = len(s["dates"])
    x_of = lambda day: x0 + (x1 - x0) * day / (n - 1)
    total = weekly([a + b for a, b in zip(s["hub"], s["lab"])])
    peak = max(c for _, c in total) or 1
    front = [(x_of(i), base - (base - top) * math.sqrt(c / peak)) for i, c in total]
    dx, dy = DEPTH
    back = [(x + dx, y + dy) for x, y in front]
    track = TRACK[name]
    faces = "".join(
        f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}L{b[0] + dx:.1f} {b[1] + dy:.1f}L{a[0] + dx:.1f} {a[1] + dy:.1f}Z"
        for a, b in zip(front, front[1:])
    )
    rungs = "".join(f"M{x:.1f} {y:.1f}l{dx} {dy}" for x, y in front)
    months = "".join(
        f'<text x="{x_of(i):.1f}" y="{base + 26}" font-family="{FONT}" font-size="12" fill="{LABEL[name]}">{datetime.date.fromisoformat(d):%b}</text>'
        for i, d in enumerate(s["dates"]) if d.endswith("-01")
    )
    stats = [(f"{s['github'] + s['gitlab']:,}", "contributions"), (f"{s['current']}d", "streak"), (f"{s['longest']}d", "best streak"), (f"{s['stars']}★", "stars")]
    row, x = "", 34
    for value, label in stats:
        row += f'<text x="{x}" y="86" font-family="{FONT}" font-size="30" font-weight="700" fill="{VALUE[name]}">{value}<tspan font-size="14" font-weight="400" fill="{LABEL[name]}" dx="8">{label}</tspan></text>'
        x += len(value) * 18 + len(label) * 7.5 + 44
    path = line(front)
    at, _ = timeline(front)
    gy, gh = 102, base - 102
    edge = [(x, y - 4) for x, y in back]
    cells, places, size = grid(s, x0, x1 + 8, gy, edge, VALUE[name])
    sky = "M0 0H" + f"{W}V{edge[-1][1]:.1f}" + "".join(f"L{x:.1f} {y:.1f}" for x, y in reversed(edge)) + f"L0 {edge[0][1]:.1f}Z"
    lift, turn, clock, motion, tilt = tricks(s, at, x_of, front)
    moments = [stage(clock(at(x_of(i)))) for i in range(len(places))]
    today = trail(places, moments, size, VALUE[name])
    updated = datetime.date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs><clipPath id="c"><path d="{shape}"/></clipPath>{defs}
<clipPath id="sky"><path d="{sky}"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="{t["bg"]}"/>{layers}</g>
<path d="{shape}" fill="none" stroke="{t["stroke"]}" stroke-width="1.5"/>
<g clip-path="url(#sky)">{cells}</g>{today}
<text x="34" y="46" font-family="{MONO}" font-size="15" fill="{LABEL[name]}"><tspan fill="{VALUE[name]}">~/</tspan>activity <tspan dx="4">· across GitHub &amp; GitLab, last year</tspan></text>
{row}{months}
<path d="{faces}" fill="{track}" fill-opacity=".1" fill-rule="nonzero"/>
<g fill="none" stroke="{track}" stroke-width="1.3" stroke-linejoin="round"><path d="{line(back)}" stroke-opacity=".7"/><path d="{rungs}" stroke-opacity=".7"/><path d="{path}" stroke-width="1.8"/></g>
{flag(*back[0], track, track, .4)}{flag(*front[0], track, track)}{flag(*back[-1], track, RED[name], .9)}{flag(*front[-1], track, RED[name], .2)}
<g>{lift}<g id="rider"><animateMotion dur="{DUR}s" repeatCount="indefinite" {motion}/><g>{tilt}<g>{turn}{rider("#f4f4f6", "#a11d2a", VALUE[name])}</g></g></g></g>
<desc>updated {updated}</desc>
</svg>"""


out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
out.mkdir(parents=True, exist_ok=True)
stats = collect(fetch(), fetch_gitlab())
for name, colors in THEMES.items():
    (out / f"stats-{name}.svg").write_text(render(stats, colors))
