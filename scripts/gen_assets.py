#!/usr/bin/env python3
"""Render every SVG card used by the profile README.

Usage: GH_TOKEN=... python3 scripts/gen_assets.py
Stats are pulled live from the GitHub GraphQL API; everything else is content
defined below. All cards share scripts/design.py.
"""
import base64
import json
import os
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from design import W, MONO, esc, open_svg, txt, rule, eyebrow_row, delay  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
LOGIN = os.environ.get("PROFILE_LOGIN", "GRJY")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

LANG_COLOR = {"Swift": "#F05138", "Python": "#3572A5", "PHP": "#4F5D95",
              "Laravel": "#FF2D20", "JavaScript": "#f1e05a", "Ruby": "#701516",
              "Blade": "#f7523f", "CSS": "#563d7c", "HTML": "#e34c26",
              "Shell": "#89e051", "C": "#555555", "TypeScript": "#3178c6"}

STEP = 45  # stagger between staggered elements, in ms


# ---------------------------------------------------------------- hero

def hero():
    h = 172
    p = open_svg(h, "Giray Akbulut — Full Stack and iOS Developer")
    p.append(txt(0, 24, "İSTANBUL, TÜRKİYE", cls="eyebrow fnt e", d=0))
    p.append(txt(0, 74, "Giray Akbulut", cls="display fg e", d=STEP))
    p.append(txt(0, 104, "Full Stack & iOS Developer  ·  Computer Engineer",
                 cls="lead mut e", d=2 * STEP))
    p.append(txt(0, 132, "Performance-critical, security-first products — on-device machine learning,",
                 cls="body fnt e", d=3 * STEP))
    p.append(txt(0, 150, "end-to-end encrypted systems, and native apps for Apple platforms.",
                 cls="body fnt e", d=3 * STEP))
    p.append(rule(0, 166, W, d=4 * STEP))
    p.append("</svg>")
    return "hero", p


# -------------------------------------------------------- capabilities

ICON = {
    "ml": ('<g fill="none" stroke="var(--muted)" stroke-width="1.4" stroke-linecap="round">'
           '<path d="M3 4.5h4M3 10h4M3 15.5h4M7 4.5 13 10M7 10h6M7 15.5 13 10M13 10h4"/></g>'
           '<g fill="var(--muted)"><circle cx="2" cy="4.5" r="1.8"/><circle cx="2" cy="10" r="1.8"/>'
           '<circle cx="2" cy="15.5" r="1.8"/><circle cx="18" cy="10" r="2.2"/></g>'),
    "lock": ('<g fill="none" stroke="var(--muted)" stroke-width="1.4">'
             '<path d="M5.6 8.4V5.8a4.4 4.4 0 0 1 8.8 0v2.6" stroke-linecap="round"/>'
             '<rect x="2.6" y="8.4" width="14.8" height="9.6" rx="2.4"/></g>'
             '<circle cx="10" cy="13.2" r="1.7" fill="var(--muted)"/>'),
    "device": ('<g fill="none" stroke="var(--muted)" stroke-width="1.4">'
               '<rect x="4.4" y="1.6" width="11.2" height="16.8" rx="2.6"/>'
               '<path d="M8.4 4.4h3.2" stroke-linecap="round"/></g>'
               '<circle cx="10" cy="15.4" r="1.2" fill="var(--muted)"/>'),
    "stack": ('<g fill="none" stroke="var(--muted)" stroke-width="1.4" '
              'stroke-linejoin="round"><path d="M10 2 18.5 6.4 10 10.8 1.5 6.4z"/>'
              '<path d="M1.5 10.4 10 14.8l8.5-4.4"/><path d="M1.5 14.2 10 18.6l8.5-4.4"/></g>'),
}

CAPS = [
    ("ml", "On-device ML",
     ["TF-IDF and logistic regression", "at ~95% accuracy, plus applied", "Keras neural networks."]),
    ("lock", "End-to-end encryption",
     ["Curve25519 key exchange with", "AES-GCM 256-bit payloads,", "under 50 ms round trip."]),
    ("device", "Native Apple apps",
     ["Swift 6 concurrency with actors,", "SwiftUI, Combine, MapKit", "and CryptoKit."]),
    ("stack", "Full-stack web",
     ["Laravel and PHP, MySQL,", "JavaScript, AWS Lambda", "and DynamoDB, REST APIs."]),
]


def capabilities():
    h = 172
    colw, gap = 202, 24
    p = open_svg(h, "What I build")
    p += eyebrow_row(0, 22, "WHAT I BUILD", W)
    for i, (icon, title, lines) in enumerate(CAPS):
        x = i * (colw + gap)
        d = STEP + i * STEP
        if i:
            p.append(f'<rect x="{x - gap // 2}" y="44" width="1" height="106" '
                     f'class="line-f e" opacity=".7"{delay(d)}/>')
        p.append(f'<g class="e"{delay(d)}>')
        p.append(f'<g transform="translate({x},46)">{ICON[icon]}</g>')
        p.append(txt(x, 94, title, cls="title fg"))
        for j, line in enumerate(lines):
            p.append(txt(x, 116 + j * 17, line, cls="small mut"))
        p.append('</g>')
    p.append("</svg>")
    return "capabilities", p


# ------------------------------------------------------------ showcase

GROUPS = [
    ("OPEN SOURCE", [
        ("PureGlass", "Swift", "★ 5", False,
         ["Liquid Glass Mac cleaner and system", "monitor for macOS 26. Fully offline."]),
        ("Purchase-Prediction ANN", "Python", "★ 1", False,
         ["Two-layer Keras network on 550K rows.", "80.5% accuracy, 0.81 AUC-ROC."]),
        ("BookFy", "PHP", "★ 1", False,
         ["Virtual library management platform", "with OpenLibrary search."]),
    ]),
    ("PRODUCTS", [
        ("TechPulse", "Swift 6", "Private", True,
         ["On-device ML news platform with", "context-preserving translation."]),
        ("Campers", "Swift", "Private", True,
         ["Safety-first camping platform. Offline", "sync and E2EE emergency comms."]),
        ("LiquidGlassKit", "Swift", "Private", True,
         ["SwiftUI component library — glass", "materials, motion, SOS module."]),
    ]),
    ("CLIENT PLATFORMS", [
        ("kozmonet", "Laravel", "kozmonet.com.tr", True,
         ["End-to-end e-commerce platform,", "designed and built solo."]),
        ("valego", "PHP", "valego.com.tr", True,
         ["Backend and infrastructure for a", "production storefront."]),
        ("iremkalkanpromakeup", "PHP", "iremkalkanpromakeup.com", True,
         ["Booking and portfolio site, designed", "and built end-to-end."]),
        ("businessturkey", "PHP", "businessturkiye.co", True,
         ["Corporate platform, designed and", "built end-to-end."]),
        ("riverra-eticaret", "Laravel", "Private", True,
         ["Drop-in e-commerce package managed", "from a central Riverra panel."]),
        (None, None, None, None,
         ["Client and product code stays closed.", "The work itself stays visible."]),
    ]),
]

CW, CH, GAP = 281, 96, 18
COLX = [0, 300, 599]


def lock_glyph(x, y, color="var(--faint)"):
    return (f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="3.6" width="7.6" height="5.6" rx="1.4" fill="{color}"/>'
            f'<path d="M1.7 3.6V2.6a2.1 2.1 0 0 1 4.2 0v1" fill="none" stroke="{color}" '
            f'stroke-width="1.1"/></g>')


def repo_card(x, y, name, lang, meta, private, lines, d):
    o = [f'<g class="e"{delay(d)}>']
    if name is None:                                    # closing note tile
        o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="8" fill="none" '
                 f'class="line-s" stroke-dasharray="4 4"/>')
        o.append(txt(x + 16, y + 30, "Private by design", cls="title mut"))
        for j, line in enumerate(lines):
            o.append(txt(x + 16, y + 52 + j * 17, line, cls="small fnt"))
        o.append('</g>')
        return o
    o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="8" class="surf line-s"/>')
    o.append(txt(x + 16, y + 28, name, cls="title " + ("mut" if private else "acc")))
    for j, line in enumerate(lines):
        o.append(txt(x + 16, y + 50 + j * 17, line, cls="small mut"))
    dot = LANG_COLOR.get(lang.split(" ")[0], "#8b949e")
    o.append(f'<circle cx="{x + 20}" cy="{y + 78}" r="4.4" fill="{dot}"/>')
    o.append(txt(x + 31, y + 82, lang, cls="small fnt"))
    if meta == "Private":
        o.append(lock_glyph(x + CW - 68, y + 74))
        o.append(txt(x + CW - 16, y + 82, "Private", cls="small fnt", anchor="end"))
    else:
        o.append(txt(x + CW - 16, y + 82, meta, cls="small fnt", anchor="end"))
    o.append('</g>')
    return o


def showcase():
    # Lay the groups out first so the canvas is exactly as tall as the content.
    layout, y = [], 22
    for label, items in GROUPS:
        top = y + 12
        layout.append((label, y, top, items))
        y = top + ((len(items) + 2) // 3) * (CH + GAP) + 34
    h = y - 34 - GAP + 10

    p = open_svg(h, "Selected work — open source, products and client platforms")
    d = 0
    for label, label_y, top, items in layout:
        p += eyebrow_row(0, label_y, label, W, d=d)
        d += STEP
        for i, item in enumerate(items):
            col, row = i % 3, i // 3
            p += repo_card(COLX[col], top + row * (CH + GAP), *item, d=d)
            d += STEP
    p.append("</svg>")
    return "showcase", p


# ------------------------------------------------------------ linkedin

LI_MARK = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 "
           "2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 "
           "4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 "
           "2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 "
           "23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z")


def linkedin():
    h = 148
    avatar = base64.b64encode((ASSETS / "avatar.png").read_bytes()).decode()
    css = ".name { font-size: 19px; font-weight: 600; letter-spacing: -0.35px; }"
    p = open_svg(h, "LinkedIn — Giray Akbulut", extra_css=css)
    p += eyebrow_row(0, 22, "LINKEDIN", W)
    p.append('<defs><clipPath id="av"><circle cx="32" cy="82" r="28"/></clipPath></defs>')
    p.append(f'<g class="e"{delay(STEP)}>')
    p.append(f'<image clip-path="url(#av)" x="4" y="54" width="56" height="56" '
             f'href="data:image/png;base64,{avatar}"/>')
    p.append('<circle cx="32" cy="82" r="28.5" fill="none" class="line-s"/>')
    p.append('</g>')
    p.append(f'<g class="e"{delay(2 * STEP)}>')
    p.append(txt(78, 74, "Giray Akbulut", cls="name fg"))
    p.append(txt(78, 96, "Full Stack & iOS Developer · Computer Engineer, Beykent 2025",
                 cls="body mut"))
    p.append(txt(78, 116, "İstanbul, Türkiye  ·  Open to freelance and full-time work",
                 cls="small fnt"))
    p.append('</g>')
    p.append(f'<g class="e"{delay(3 * STEP)}>')
    p.append('<rect x="676" y="64" width="204" height="38" rx="8" class="surf line-s"/>')
    p.append('<g transform="translate(696,75) scale(0.62)">'
             f'<path d="{LI_MARK}" fill="var(--accent)"/></g>')
    p.append(txt(714, 88, "Connect on LinkedIn", cls="body acc",
                 extra=' font-weight="600"'))
    p.append('<path d="M856 82.5h6m-2.6-2.8 2.8 2.8-2.8 2.8" fill="none" stroke="var(--accent)" '
             'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append('</g>')
    p.append(rule(0, 138, W, d=4 * STEP))
    p.append("</svg>")
    return "linkedin", p


# --------------------------------------------------------------- stats

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch_stats():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "grjy-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def stats(user):
    nodes = user["repositories"]["nodes"]
    sizes, colors = {}, {}
    for repo in nodes:
        for edge in repo["languages"]["edges"]:
            n = edge["node"]["name"]
            sizes[n] = sizes.get(n, 0) + edge["size"]
            colors[n] = edge["node"]["color"] or "#8b949e"
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:5]
    total = sum(s for _, s in top) or 1

    stars = sum(r["stargazerCount"] for r in nodes)
    repos = user["repositories"]["totalCount"]
    followers = user["followers"]["totalCount"]
    contribs = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    def plural(n, one, many):
        return one if n == 1 else many

    metrics = [(repos, plural(repos, "Public repository", "Public repositories")),
               (stars, plural(stars, "Total star", "Total stars")),
               (contribs, "Contributions, past year"),
               (followers, plural(followers, "Follower", "Followers"))]

    h = 168
    p = open_svg(h, "GitHub activity")
    p += eyebrow_row(0, 22, "GITHUB", W)
    for i, (value, label) in enumerate(metrics):
        x = i * 226
        p.append(f'<g class="e"{delay(STEP + i * STEP)}>')
        p.append(txt(x, 76, str(value), cls="metric fg"))
        p.append(txt(x, 96, label, cls="small fnt"))
        p.append('</g>')

    bar_y = 118
    p.append(f'<g class="grow"{delay(3 * STEP)}>')
    p.append(f'<defs><clipPath id="barclip"><rect x="0" y="{bar_y}" width="{W}" height="6" rx="3"/>'
             f'</clipPath></defs>')
    p.append('<g clip-path="url(#barclip)">')
    cursor = 0.0
    for name, size in top:
        seg = W * size / total
        p.append(f'<rect x="{cursor:.1f}" y="{bar_y}" width="{max(seg, 2):.1f}" height="6" '
                 f'fill="{colors[name]}"/>')
        cursor += seg
    p.append('</g></g>')

    lx = 0
    for i, (name, size) in enumerate(top):
        label = f"{name} {100.0 * size / total:.1f}%"
        p.append(f'<g class="e"{delay(4 * STEP + i * 30)}>')
        p.append(f'<circle cx="{lx + 4}" cy="{bar_y + 26}" r="4" fill="{colors[name]}"/>')
        p.append(txt(lx + 15, bar_y + 30, label, cls="small fnt"))
        p.append('</g>')
        lx += 30 + int(6.4 * len(label))
    p.append(f'<text x="{W}" y="{bar_y + 30}" class="small fnt mono" text-anchor="end" '
             f'opacity=".8">updated daily</text>')
    p.append("</svg>")
    return "stats", p


def write(name, parts):
    path = ASSETS / f"{name}.svg"
    path.write_text("\n".join(parts) + "\n")
    print(f"  {path.relative_to(ROOT)}  ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    print("rendering cards:")
    for builder in (hero, capabilities, showcase, linkedin):
        write(*builder())
    if TOKEN:
        write(*stats(fetch_stats()))
    else:
        print("  skipping stats.svg (no GH_TOKEN)")
