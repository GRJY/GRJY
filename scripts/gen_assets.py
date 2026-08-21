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
from design import (W, MONO, base_css, esc, open_svg, txt, rule, eyebrow_row,  # noqa: E402
                    delay)

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

def hero(theme):
    h = 172
    p = open_svg(h, "Giray Akbulut — Full Stack and iOS Developer", theme)
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


def capabilities(theme):
    h = 172
    colw, gap = 202, 24
    p = open_svg(h, "What I build", theme)
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




# ------------------------------------------------------------- flagship

APPLE = ("M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 "
         "3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 "
         "3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 "
         "1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 "
         "2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09")

FLAGSHIP = [
    ("app-valego.png", "Valego", "Valet, parking, wash and transfer in one panel",
     ["Corporate valet platform — QR handover, live vehicle tracking and a",
      "single operations panel for hotels, malls and residences."],
     "Laravel", "Laravel · Flutter · MySQL", "854 commits"),
    ("app-businessturkey.png", "Business Turkey", "B2B platform, web and mobile",
     ["Corporate B2B platform with a central management console and a",
      "companion mobile app for member companies."],
     "PHP", "PHP · Laravel · TypeScript · Flutter", "811 commits"),
]


def platform_row(x, y, accent="var(--faint)"):
    """Apple mark, an Android-ish handset and a globe — where the product ships."""
    o = [f'<g transform="translate({x},{y})" fill="none" stroke="{accent}" stroke-width="1.3">']
    o.append(f'<path d="{APPLE}" fill="{accent}" stroke="none" transform="scale(0.52)"/>')
    o.append('<rect x="20" y="1.5" width="9" height="11" rx="2.2"/>')
    o.append(f'<circle cx="22.6" cy="4.6" r=".7" fill="{accent}" stroke="none"/>')
    o.append(f'<circle cx="26.4" cy="4.6" r=".7" fill="{accent}" stroke="none"/>')
    o.append('<circle cx="41" cy="7" r="5.6"/>')
    o.append('<ellipse cx="41" cy="7" rx="2.4" ry="5.6"/>')
    o.append('<path d="M35.6 7h10.8"/>')
    o.append('</g>')
    return o


def flagship(theme):
    h = 212
    card_w, card_h, card_y = 431, 152, 44
    p = open_svg(h, "Flagship work — Valego and Business Turkey", theme)
    p += eyebrow_row(0, 22, "FLAGSHIP WORK", W)
    icons = {}
    for i, (icon, title, sub, lines, lang, stack, commits) in enumerate(FLAGSHIP):
        x = i * (card_w + 18)
        d = STEP + i * STEP
        data = base64.b64encode((ASSETS / icon).read_bytes()).decode()
        p.append(f'<defs><clipPath id="ic{i}">'
                 f'<rect x="{x + 18}" y="{card_y + 18}" width="48" height="48" rx="11"/>'
                 f'</clipPath></defs>')
        p.append(f'<g class="e"{delay(d)}>')
        p.append(f'<rect x="{x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" '
                 f'class="surf line-s"/>')
        p.append(f'<image clip-path="url(#ic{i})" x="{x + 18}" y="{card_y + 18}" '
                 f'width="48" height="48" href="data:image/png;base64,{data}"/>')
        p.append(f'<rect x="{x + 18}" y="{card_y + 18}" width="48" height="48" rx="11" '
                 f'fill="none" class="line-s"/>')
        p.append(txt(x + 78, card_y + 42, title, cls="lead fg"))
        p.append(txt(x + 78, card_y + 62, sub, cls="small fnt"))
        for j, line in enumerate(lines):
            p.append(txt(x + 18, card_y + 92 + j * 17, line, cls="small mut"))
        dot = LANG_COLOR.get(lang, "#8b949e")
        p.append(f'<circle cx="{x + 22}" cy="{card_y + 130}" r="4.4" fill="{dot}"/>')
        p.append(txt(x + 33, card_y + 134, stack, cls="small fnt"))
        p.append(txt(x + card_w - 18, card_y + 134, commits, cls="small fnt", anchor="end"))
        p += platform_row(x + card_w - 66, card_y + 26)
        p.append('</g>')
    p.append("</svg>")
    return "flagship", p



# ---------------------------------------------------------------- chips

GLOBE = ('<circle cx="8" cy="8" r="7" fill="none" stroke="var(--muted)" stroke-width="1.3"/>'
         '<ellipse cx="8" cy="8" rx="3" ry="7" fill="none" stroke="var(--muted)" stroke-width="1.3"/>'
         '<path d="M1.4 8h13.2" stroke="var(--muted)" stroke-width="1.3"/>')
APPLE_MARK = (f'<path d="{APPLE}" fill="var(--muted)" transform="translate(-1.2,0) scale(0.68)"/>')
PLAY = ('<path d="M2.6 1.4 12.4 8 2.6 14.6z" fill="none" stroke="var(--muted)" '
        'stroke-width="1.3" stroke-linejoin="round"/>')

CHIPS = [
    ("chip-valego-web", "valego.com.tr", GLOBE),
    ("chip-valego-ios", "App Store", APPLE_MARK),
    ("chip-valego-play", "Google Play", PLAY),
    ("chip-bt-web", "businessturkiye.co", GLOBE),
    ("chip-bt-ios", "App Store", APPLE_MARK),
    ("chip-bt-play", "Google Play", PLAY),
]


def chip(name, label, icon, theme):
    """A single link, drawn to the same spec as the cards it sits under."""
    w = 44 + int(6.85 * len(label))
    h = 34
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">',
         f'<style>{base_css(theme)}</style>',
         f'<rect width="{w}" height="{h}" class="canvas"/>',
         f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="9" '
         f'class="surf line-s"/>',
         f'<g transform="translate(13,9)">{icon}</g>',
         txt(34, 22, label, cls="body fg"),
         '</svg>']
    return name, p


# ----------------------------------------------------------------- apps

SCREENS = [
    ("screen-4558.jpg", "Valego Kurumsal", "Launch"),
    ("screen-4559.jpg", "Valego Kurumsal", "Operations dashboard"),
    ("screen-4561.jpg", "Business Turkey", "Onboarding"),
    ("screen-4560.jpg", "Business Turkey", "Marketplace feed"),
]

PHONE_W = 190
PHONE_H = 414          # 19.5:9, the iPhone aspect the screenshots were taken at
PHONE_GAP = 22


def apps(theme):
    top = 46
    caption = top + PHONE_H + 26
    h = caption + 38
    left = (W - (len(SCREENS) * PHONE_W + (len(SCREENS) - 1) * PHONE_GAP)) // 2

    p = open_svg(h, "Shipped apps — Valego Kurumsal and Business Turkey on iOS", theme)
    p += eyebrow_row(0, 22, "SHIPPED TO THE APP STORE", W)
    for i, (shot, app, screen) in enumerate(SCREENS):
        x = left + i * (PHONE_W + PHONE_GAP)
        data = base64.b64encode((ASSETS / shot).read_bytes()).decode()
        p.append(f'<defs><clipPath id="sc{i}">'
                 f'<rect x="{x + 5}" y="{top + 5}" width="{PHONE_W - 10}" '
                 f'height="{PHONE_H - 10}" rx="22"/></clipPath></defs>')
        p.append(f'<g class="e"{delay(STEP + i * STEP)}>')
        p.append(f'<rect x="{x}" y="{top}" width="{PHONE_W}" height="{PHONE_H}" rx="27" '
                 f'class="surf line-s" stroke-width="1.5"/>')
        p.append(f'<image clip-path="url(#sc{i})" x="{x + 5}" y="{top + 5}" '
                 f'width="{PHONE_W - 10}" height="{PHONE_H - 10}" '
                 f'preserveAspectRatio="xMidYMid slice" '
                 f'href="data:image/jpeg;base64,{data}"/>')
        # Dynamic Island, so the frame reads as the device the screenshot came from.
        p.append(f'<rect x="{x + PHONE_W // 2 - 24}" y="{top + 13}" width="48" height="13" '
                 f'rx="6.5" fill="#000000"/>')
        mid = x + PHONE_W // 2
        p.append(txt(mid, caption, app, cls="title fg", anchor="middle"))
        p.append(txt(mid, caption + 17, screen, cls="small fnt", anchor="middle"))
        p.append('</g>')
    p.append("</svg>")
    return "apps", p


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
    ("AGENCY WORK  ·  ATOMEDYA", [
        ("Internal consoles", "TypeScript · Blade", "Private", True,
         ["Operations and quoting panels used", "across the agency. 599 commits."]),
        ("Social platform", "PHP · Flutter", "Private", True,
         ["Feed, campaigns and messaging for", "a consumer product. 191 commits."]),
        ("E-commerce platform", "Blade · MySQL", "Private", True,
         ["Storefront, catalogue and checkout,", "built end-to-end. 96 commits."]),
        ("Booking platform", "PHP · MySQL", "Private", True,
         ["Appointments, portfolio and admin", "for a studio brand. 93 commits."]),
        ("E-commerce package", "Laravel", "Private", True,
         ["Drop-in storefront driven from a", "central agency panel. 40 commits."]),
        (None, None, None, None, []),
    ]),
]

# Ranked by commits authored in the past year. Only projects whose product is
# already public are named; the rest of the agency work stays as a count.
PRIVATE_WORK = [
    ("Valet platform", "854 commits"), ("B2B platform", "811 commits"),
    ("Internal consoles", "599 commits"), ("Social platform", "191 commits"),
    ("E-commerce platform", "96 commits"), ("Booking platform", "93 commits"),
    ("E-commerce package", "40 commits"), ("On-device ML app", "27 commits"),
]

# The one deliberate loop on the page: the private projects have no repository to
# link to, so the tile cycles them instead. Blur bridges the two states so the
# swap reads as one line changing rather than two lines overlapping.
TICKER_CSS = """
  .tick { opacity: 0; animation: tick %(cycle)sms linear infinite;
          transform-box: fill-box; }
  @keyframes tick {
    0%%      { opacity: 0; transform: translateY(5px); filter: blur(2px); }
    2%%      { opacity: 1; transform: translateY(0);   filter: blur(0); }
    %(hold)s%% { opacity: 1; transform: translateY(0);   filter: blur(0); }
    %(out)s%%  { opacity: 0; transform: translateY(-5px); filter: blur(2px); }
    100%%    { opacity: 0; transform: translateY(-5px); filter: blur(2px); }
  }
  .march { animation: march 24s linear infinite; }
  @keyframes march { to { stroke-dashoffset: -32; } }
  @media (prefers-reduced-motion: reduce) {
    .tick, .march { animation: none; }
    .tick:first-of-type { opacity: 1; }
  }
"""


def ticker_css():
    slot = 100.0 / len(PRIVATE_WORK)
    return TICKER_CSS % {"cycle": len(PRIVATE_WORK) * 2400,
                         "hold": round(slot - 2, 2), "out": round(slot, 2)}


CW, CH, GAP = 281, 96, 18
COLX = [0, 300, 599]


def lock_glyph(x, y, color="var(--faint)"):
    return (f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="3.6" width="7.6" height="5.6" rx="1.4" fill="{color}"/>'
            f'<path d="M1.7 3.6V2.6a2.1 2.1 0 0 1 4.2 0v1" fill="none" stroke="{color}" '
            f'stroke-width="1.1"/></g>')


def repo_card(x, y, name, lang, meta, private, lines, d):
    o = [f'<g class="e"{delay(d)}>']
    if name is None:                                    # private-work ticker
        o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="8" fill="none" '
                 f'class="line-s march" stroke-dasharray="4 4"/>')
        o.append(txt(x + 16, y + 30, "27 private repositories", cls="title mut"))
        o.append(txt(x + 16, y + 50, "3,025 commits in the past year.",
                     cls="small fnt"))
        cycle = len(PRIVATE_WORK) * 2400
        for j, (proj, stack) in enumerate(PRIVATE_WORK):
            o.append(f'<g class="tick" style="animation-delay:{j * 2400}ms">')
            o.append(lock_glyph(x + 16, y + 70))
            o.append(txt(x + 30, y + 78, proj, cls="small mut"))
            o.append(txt(x + CW - 16, y + 78, stack, cls="small fnt", anchor="end"))
            o.append('</g>')
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


def showcase(theme):
    # Lay the groups out first so the canvas is exactly as tall as the content.
    layout, y = [], 22
    for label, items in GROUPS:
        top = y + 12
        layout.append((label, y, top, items))
        y = top + ((len(items) + 2) // 3) * (CH + GAP) + 34
    h = y - 34 - GAP + 10

    p = open_svg(h, "Selected work — open source, products and client platforms",
                 theme, extra_css=ticker_css())
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


def linkedin(theme):
    h = 148
    avatar = base64.b64encode((ASSETS / "avatar.png").read_bytes()).decode()
    css = ".name { font-size: 19px; font-weight: 600; letter-spacing: -0.35px; }"
    p = open_svg(h, "LinkedIn — Giray Akbulut", theme, extra_css=css)
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



# ----------------------------------------------------------- credentials

STACK = [
    ("Languages", "Swift · Python · JavaScript · PHP · Java · C++"),
    ("Apple", "SwiftUI · Swift 6 Concurrency · Combine · CryptoKit · MapKit"),
    ("Web & cloud", "Laravel · MySQL · AWS Lambda · DynamoDB · Supabase · REST"),
    ("Machine learning", "Keras · scikit-learn · TF-IDF · Core ML"),
    ("Design", "Figma · Framer"),
]

CERTS = [
    ("Full Stack Developer", "Meta"),
    ("AI Engineering", "IBM"),
    ("Cloud Practitioner", "Amazon Web Services"),
    ("UX Design", "Google"),
    ("PCEP — Entry-Level Python", "Python Institute"),
    ("Java Foundations", "Oracle"),
    ("Python Coder (GPYC)", "GIAC"),
]


def credentials(theme):
    row_h, label_w = 34, 150
    stack_top = 40
    cert_label_y = stack_top + len(STACK) * row_h + 46
    cert_top = cert_label_y + 18
    cert_rows = (len(CERTS) + 1) // 2
    h = cert_top + cert_rows * 42 + 6

    p = open_svg(h, "Stack and certifications", theme)
    p += eyebrow_row(0, 22, "STACK", W)
    for i, (label, items) in enumerate(STACK):
        y = stack_top + i * row_h
        d = STEP + i * STEP
        p.append(f'<g class="e"{delay(d)}>')
        p.append(txt(0, y + 22, label, cls="small fnt"))
        p.append(txt(label_w, y + 22, items, cls="body mut"))
        if i < len(STACK) - 1:
            p.append(f'<rect x="0" y="{y + row_h - 1}" width="{W}" height="1" '
                     f'class="line-f" opacity=".55"/>')
        p.append('</g>')

    p += eyebrow_row(0, cert_label_y, "CERTIFICATIONS", W, d=6 * STEP)
    for i, (name, issuer) in enumerate(CERTS):
        col, row = i % 2, i // 2
        x = col * 452
        y = cert_top + row * 42
        p.append(f'<g class="e"{delay(7 * STEP + i * 30)}>')
        p.append(f'<path d="M{x + 1} {y + 12}v14" class="line-s" stroke-width="2" '
                 f'stroke-linecap="round"/>')
        p.append(txt(x + 14, y + 18, name, cls="body fg"))
        p.append(txt(x + 14, y + 34, issuer, cls="small fnt"))
        p.append('</g>')
    p.append("</svg>")
    return "credentials", p


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


def stats(user, theme):
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

    cache_path = ASSETS / "commit-days.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    if cache:
        # Commit history reaches private and organisation repositories; the
        # public GraphQL slice does not, and understates the work badly.
        metrics = [(cache["repos"], "Repositories worked in"),
                   (cache["private"], "Private repositories"),
                   (repos, plural(repos, "Public repository", "Public repositories")),
                   (stars, plural(stars, "Total star", "Total stars"))]
        if cache.get("languages"):
            sizes = cache["languages"]
            colors = {n: LANG_COLOR.get(n, "#8b949e") for n in sizes}
            top = sorted(sizes.items(), key=lambda kv: -kv[1])[:5]
            total = sum(s for _, s in top) or 1
    else:
        metrics = [(repos, plural(repos, "Public repository", "Public repositories")),
                   (stars, plural(stars, "Total star", "Total stars")),
                   (contribs, "Contributions, past year"),
                   (followers, plural(followers, "Follower", "Followers"))]

    h = 168
    p = open_svg(h, "GitHub activity", theme)
    p += eyebrow_row(0, 22, "LANGUAGE MIX  ·  ALL REPOSITORIES", W)
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
    user = fetch_stats() if TOKEN else None
    for theme in ("dark", "light"):
        for builder in (hero, capabilities, flagship, apps, showcase, linkedin,
                        credentials):
            name, parts = builder(theme)
            write(f"{name}-{theme}", parts)
        for chip_name, label, icon in CHIPS:
            name, parts = chip(chip_name, label, icon, theme)
            write(f"{name}-{theme}", parts)
        if user:
            name, parts = stats(user, theme)
            write(f"{name}-{theme}", parts)
    if not user:
        print("  skipping stats card (no GH_TOKEN)")
