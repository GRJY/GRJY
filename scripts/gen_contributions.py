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


def rnd(*seed):
    """Deterministic jitter — the same grid must render the same every run."""
    h = 2166136261
    for value in seed:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h / 0xFFFFFFFF


# Eight scatter vectors for the cell fragments and six for the finer ash, all
# blowing up and to the right so the whole year drifts on one wind.
FRAGMENTS = [(26, -11, -30), (38, -19, 36), (31, -26, -12), (47, -13, 50),
             (22, -20, 16), (43, -28, -40), (54, -16, 27), (34, -8, -48)]

# (dx, dy, lingers) — a few specks ride the wind further and fade late, so the
# air still has ash in it after the burst has gone.
MOTES = [(72, -26, False), (88, -17, False), (63, -34, False),
         (104, -29, True), (81, -41, True), (69, -13, True)]

BURST = "cubic-bezier(.5,.05,.92,.35)"      # dust accelerates as the wind takes it
RETURN = "cubic-bezier(.23,1,.32,1)"        # and decelerates as it settles back


def motion_css():
    # 9s cycle: solid until 30%, dust by 44%, back by 74%. The first burst lands
    # under three seconds after the image loads instead of after eight.
    css = ["""
  .g { animation-duration: 9s; animation-iteration-count: infinite;
       transform-box: fill-box; transform-origin: center; }
  .core { animation-name: core; }
  @keyframes core {
    0%, 30%    { opacity: 1; transform: none; }
    32%        { opacity: 1; transform: scale(1.16); }
    37%        { opacity: 0; transform: scale(.9); }
    58%        { opacity: 0; transform: scale(.9); }
    74%, 100%  { opacity: 1; transform: none; }
  }
  .ash { animation-name: ash; }
  @keyframes ash {
    0%, 30%   { opacity: 1; transform: none;
                animation-timing-function: BURST_C; }
    32%       { opacity: 1; transform: scale(1.14); }
    44%       { opacity: 0; transform: translate(17px,-13px) scale(.22); }
    58%       { opacity: 0; transform: translate(17px,-13px) scale(.22);
                animation-timing-function: RETURN_C; }
    74%, 100% { opacity: 1; transform: none; }
  }
""".replace("BURST_C", BURST).replace("RETURN_C", RETURN)]

    for i, (dx, dy, rot) in enumerate(FRAGMENTS):
        css.append(f"""
  .f{i} {{ animation-name: f{i}; }}
  @keyframes f{i} {{
    0%, 30%  {{ opacity: 1; transform: none;
                animation-timing-function: {BURST}; }}
    32%      {{ opacity: 1; transform: translate({dx * 0.05:.1f}px,{dy * 0.05:.1f}px)
                           rotate({rot * 0.06:.1f}deg); }}
    48%      {{ opacity: 0; transform: translate({dx}px,{dy}px) rotate({rot}deg) scale(.26); }}
    58%      {{ opacity: 0; transform: translate({dx}px,{dy}px) rotate({rot}deg) scale(.26);
                animation-timing-function: {RETURN}; }}
    74%, 100% {{ opacity: 1; transform: none; }}
  }}""")

    for i, (dx, dy, lingers) in enumerate(MOTES):
        gone = 66 if lingers else 53
        peak = ".55" if lingers else ".85"
        css.append(f"""
  .m{i} {{ animation-name: m{i}; }}
  @keyframes m{i} {{
    0%, 31%  {{ opacity: 0; transform: none;
                animation-timing-function: {BURST}; }}
    34%      {{ opacity: {peak}; transform: translate({dx * 0.1:.1f}px,{dy * 0.1:.1f}px); }}
    {gone}%  {{ opacity: 0; transform: translate({dx}px,{dy}px) scale(.12); }}
    100%     {{ opacity: 0; transform: translate({dx}px,{dy}px) scale(.12); }}
  }}""")

    css.append("""
  @media (prefers-reduced-motion: reduce) {
    .g { animation: none; }
    [class*="m"].g { opacity: 0; }
  }
""")
    return "".join(css)


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

    p = open_svg(h, f"{total} commits in the past year, private work included",
                 theme, extra_css=motion_css())
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
            colour = colors[lv]
            # The dissolve front sweeps left to right, ragged rather than ruled.
            wave = int(w * 21 + d * 5 + rnd(w, d, 7) * 150)

            if lv == 0:
                p.append(f'<rect class="g ash" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                         f'rx="2.5" fill="{colour}" style="animation-delay:{wave}ms"/>')
                continue

            # A day with commits comes apart into quarters, each on its own wind.
            p.append(f'<rect class="g core" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                     f'rx="2.5" fill="{colour}" style="animation-delay:{wave}ms">'
                     f'<title>{day.isoformat()}: {count} commits</title></rect>')
            for k, (fx, fy) in enumerate(((0.5, 0.5), (5.5, 0.5), (0.5, 5.5), (5.5, 5.5))):
                variant = int(rnd(w, d, k) * len(FRAGMENTS))
                lag = wave + int(rnd(w, d, k, 3) * 70)
                p.append(f'<rect class="g f{variant}" x="{x + fx}" y="{y + fy}" width="5" '
                         f'height="5" rx="1.2" fill="{colour}" '
                         f'style="animation-delay:{lag}ms"/>')
            for k in range(3 + (lv >= 3)):
                variant = int(rnd(w, d, k, 11) * len(MOTES))
                cx = x + 2 + rnd(w, d, k, 17) * (CELL - 4)
                cy = y + 2 + rnd(w, d, k, 23) * (CELL - 4)
                r = 1 + rnd(w, d, k, 29) * 1.3
                lag = wave + int(rnd(w, d, k, 31) * 110)
                p.append(f'<circle class="g m{variant}" cx="{cx:.1f}" cy="{cy:.1f}" '
                         f'r="{r:.1f}" fill="{colour}" style="animation-delay:{lag}ms"/>')

    legend_y = grid_top + 7 * PITCH + 22
    p.append(f'<g class="e"{delay(180)}>')
    p.append(txt(GRID_X, legend_y, "Every square is a day. The snap sweeps the year, then it all comes back.",
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
