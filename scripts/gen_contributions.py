#!/usr/bin/env python3
"""Render the contribution grid from real commit history, private work included.

GitHub's contribution calendar API hides private activity unless the token
carries `read:user`, so this walks the commit history of every repository the
token can reach instead — personal, organisation and collaborator alike — and
counts commits authored by the profile owner.

Usage: GH_TOKEN=... python3 scripts/gen_contributions.py
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from design import W, esc, open_svg, txt, eyebrow_row, delay  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
LOGIN = os.environ.get("PROFILE_LOGIN", "GRJY")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
CACHE = ASSETS / "commit-days.json"

CELL, GAP = 11, 3
PITCH = CELL + GAP
WEEKS = 53
GRID_X, LABEL_W = 34, 34

SCALE = {
    "dark":  ["#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"],
    "light": ["#eff2f5", "#aceebb", "#4ac26b", "#2da44e", "#116329"],
}


def api(path, params=None):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"bearer {TOKEN}", "Accept": "application/vnd.github+json",
        "User-Agent": "grjy-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), r.headers.get("Link", "")


def all_repos():
    seen = {}
    for affiliation in ("owner", "organization_member", "collaborator"):
        page = 1
        while True:
            data, _ = api("/user/repos", {"affiliation": affiliation,
                                          "per_page": 100, "page": page})
            if not data:
                break
            for repo in data:
                seen[repo["full_name"]] = repo["private"]
            page += 1
    return seen


def commit_days(since):
    days, active = {}, {}
    repos = all_repos()
    print(f"scanning {len(repos)} repositories for commits by {LOGIN}")
    for full_name in sorted(repos):
        page, found = 1, 0
        while True:
            try:
                data, _ = api(f"/repos/{full_name}/commits",
                              {"author": LOGIN, "since": since, "per_page": 100,
                               "page": page})
            except urllib.error.HTTPError as err:
                if err.code in (409, 404, 403):     # empty or unreadable repo
                    break
                raise
            if not data:
                break
            for commit in data:
                date = (commit["commit"]["author"] or {}).get("date", "")[:10]
                if date:
                    days[date] = days.get(date, 0) + 1
                    found += 1
            if len(data) < 100:
                break
            page += 1
        if found:
            active[full_name] = repos[full_name]
            print(f"  {full_name}: {found}{' (private)' if repos[full_name] else ''}")
    return days, active


def build(days, theme, total, since_date, private_repos):
    colors = SCALE[theme]
    counts = sorted(c for c in days.values() if c)
    if counts:
        q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)]
    else:
        q = [1, 2, 3]

    def level(count):
        if not count:
            return 0
        if count <= q[0]:
            return 1
        if count <= q[1]:
            return 2
        if count <= q[2]:
            return 3
        return 4

    # The grid starts on the Sunday on or before the first day shown.
    start = since_date - dt.timedelta(days=(since_date.weekday() + 1) % 7)
    grid_top = 104
    h = grid_top + 7 * PITCH + 44

    css = """
  .cell { animation: dust 11s cubic-bezier(.4,0,.2,1) infinite;
          transform-box: fill-box; transform-origin: center; }
  @keyframes dust {
    0%, 50% { opacity: 1; transform: translate(0,0) scale(1); }
    62%     { opacity: 0; transform: translate(15px,-13px) scale(.18); }
    88%     { opacity: 0; transform: translate(15px,-13px) scale(.18); }
    100%    { opacity: 1; transform: translate(0,0) scale(1); }
  }
  .mote { opacity: 0; animation: mote 11s cubic-bezier(.4,0,.2,1) infinite;
          transform-box: fill-box; transform-origin: center; }
  @keyframes mote {
    0%, 50% { opacity: 0; transform: translate(0,0) scale(1); }
    56%     { opacity: .85; }
    72%     { opacity: 0; transform: translate(34px,-30px) scale(.2); }
    100%    { opacity: 0; transform: translate(34px,-30px) scale(.2); }
  }
  @media (prefers-reduced-motion: reduce) {
    .cell, .mote { animation: none; }
    .mote { opacity: 0; }
  }
"""
    p = open_svg(h, f"{total} commits in the past year, private work included",
                 theme, extra_css=css)
    p += eyebrow_row(0, 22, "COMMITS, PAST YEAR", W)
    p.append(txt(0, 58, f"{total:,}", cls="metric fg", d=45))
    label_x = 20 + 18 * len(f"{total:,}")
    p.append(txt(label_x, 58, "commits across public and private repositories",
                 cls="body mut", d=45))
    p.append(txt(label_x, 76, f"{private_repos} of them private — agency, client and product work",
                 cls="small fnt", d=90))

    months, last_month = [], None
    for w in range(WEEKS):
        day = start + dt.timedelta(days=w * 7)
        if day.month != last_month and day.day <= 7:
            months.append((w, day.strftime("%b")))
            last_month = day.month

    p.append(f'<g class="e"{delay(135)}>')
    for w, name in months:
        p.append(txt(GRID_X + w * PITCH, grid_top - 8, name, cls="small fnt"))
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(txt(0, grid_top + row * PITCH + 9, name, cls="small fnt"))
    p.append('</g>')

    today = dt.date.today()
    for w in range(WEEKS):
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            if day > today:
                continue
            count = days.get(day.isoformat(), 0)
            lv = level(count)
            x = GRID_X + w * PITCH
            y = grid_top + d * PITCH
            # Columns disintegrate left to right, so the snap sweeps the year.
            wave = w * 42 + d * 9
            p.append(f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                     f'rx="2.5" fill="{colors[lv]}" style="animation-delay:{wave}ms">'
                     f'<title>{day.isoformat()}: {count} commits</title></rect>')
            if lv >= 3:
                for k in (0, 1):
                    p.append(f'<circle class="mote" cx="{x + 3 + k * 5}" cy="{y + 4 + k * 4}" '
                             f'r="1.4" fill="{colors[lv]}" '
                             f'style="animation-delay:{wave + 60 + k * 90}ms"/>')

    legend_y = grid_top + 7 * PITCH + 22
    p.append(f'<g class="e"{delay(180)}>')
    p.append(txt(GRID_X, legend_y, "Every square is a day. The snap runs left to right.",
                 cls="small fnt"))
    p.append(txt(W - 124, legend_y, "Less", cls="small fnt", anchor="end"))
    for i, color in enumerate(colors):
        p.append(f'<rect x="{W - 116 + i * 15}" y="{legend_y - 9}" width="{CELL}" '
                 f'height="{CELL}" rx="2.5" fill="{color}"/>')
    p.append(txt(W, legend_y, "More", cls="small fnt", anchor="end"))
    p.append('</g>')
    p.append("</svg>")
    return p


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("GH_TOKEN is required")
    since_date = dt.date.today() - dt.timedelta(days=364)
    days, active = commit_days(since_date.isoformat() + "T00:00:00Z")
    total = sum(days.values())
    private = sum(1 for is_private in active.values() if is_private)

    languages = {}
    for full_name in active:
        try:
            data, _ = api(f"/repos/{full_name}/languages")
        except urllib.error.HTTPError:
            continue
        for name, size in data.items():
            languages[name] = languages.get(name, 0) + size

    CACHE.write_text(json.dumps({"days": days, "total": total,
                                 "repos": len(active), "private": private,
                                 "languages": languages},
                                sort_keys=True, indent=0))
    print(f"total commits: {total} across {len(days)} active days, "
          f"{len(active)} repositories ({private} private)")
    for theme in ("dark", "light"):
        parts = build(days, theme, total, since_date, private)
        path = ASSETS / f"contributions-{theme}.svg"
        path.write_text("\n".join(parts) + "\n")
        print(f"  {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
