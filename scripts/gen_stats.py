#!/usr/bin/env python3
"""Generate assets/stats.svg — a self-hosted, animated GitHub stats card.

Reads public profile data via the GitHub GraphQL API (token from GH_TOKEN or
GITHUB_TOKEN) and renders a glass-styled card with animated bars and counters.
"""
import json
import os
import pathlib
import urllib.request

LOGIN = os.environ.get("PROFILE_LOGIN", "GRJY")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "stats.svg"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
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

FALLBACK = {"#": "unknown"}


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "grjy-profile-stats",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(user):
    repos = user["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    repo_count = user["repositories"]["totalCount"]
    followers = user["followers"]["totalCount"]
    contributions = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    sizes = {}
    colors = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            sizes[name] = sizes.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8ea2ff"
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    total = sum(s for _, s in top) or 1

    metrics = [
        ("Public repos", repo_count),
        ("Total stars", stars),
        ("Contributions (1y)", contributions),
        ("Followers", followers),
    ]

    W, H = 880, 250
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="GitHub statistics for {esc(LOGIN)}">'
    )
    parts.append("""<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#0c1122"/><stop offset="100%" stop-color="#080b17"/>
  </linearGradient>
  <linearGradient id="sedge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.26"/>
    <stop offset="50%" stop-color="#ffffff" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0.14"/>
  </linearGradient>
  <clipPath id="scard"><rect x="1" y="1" width="878" height="248" rx="24"/></clipPath>
  <style>
    .f { font-family: ui-sans-serif, -apple-system, "SF Pro Text", "Segoe UI", Inter, Helvetica, Arial, sans-serif; }
    .mono { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }
    .in { opacity: 0; animation: in 14s ease-out infinite; transform-box: fill-box; }
    @keyframes in {
      0%   { opacity: 0; transform: translateY(10px); }
      5%   { opacity: 1; transform: translateY(0); }
      92%  { opacity: 1; transform: translateY(0); }
      98%  { opacity: 0; transform: translateY(-6px); }
      100% { opacity: 0; transform: translateY(-6px); }
    }
    .bar { animation: grow 14s cubic-bezier(.22,1,.36,1) infinite; transform-box: fill-box; transform-origin: left center; }
    @keyframes grow {
      0%   { transform: scaleX(0); }
      12%  { transform: scaleX(1); }
      94%  { transform: scaleX(1); }
      100% { transform: scaleX(0); }
    }
    .sweep3 { animation: sw3 14s cubic-bezier(.4,0,.2,1) infinite; }
    @keyframes sw3 {
      0% { transform: translateX(-300px) } 14% { transform: translateX(1010px) } 100% { transform: translateX(1010px) }
    }
    @media (prefers-reduced-motion: reduce) {
      .in, .bar, .sweep3 { animation: none } .in { opacity: 1 }
    }
  </style>
</defs>""")
    parts.append('<g clip-path="url(#scard)">')
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#sbg)"/>')
    parts.append('<rect class="sweep3" x="-160" y="-40" width="130" height="340" fill="#ffffff" fill-opacity=".05" transform="skewX(-16)"/>')
    parts.append("</g>")
    parts.append('<rect x="1" y="1" width="878" height="248" rx="24" fill="none" stroke="url(#sedge)" stroke-width="1.5"/>')
    parts.append('<text class="f mono" x="44" y="40" fill="#5b6789" font-size="11.5" letter-spacing="2.4">GITHUB AT A GLANCE</text>')

    # metric tiles
    for i, (label, value) in enumerate(metrics):
        x = 44 + i * 122
        delay = 0.10 + i * 0.10
        parts.append(
            f'<g class="f in" style="animation-delay:{delay:.2f}s">'
            f'<text x="{x}" y="94" fill="#f1f5ff" font-size="34" font-weight="700">{value}</text>'
            f'<text x="{x}" y="116" fill="#7f8db3" font-size="11.5">{esc(label)}</text>'
            f"</g>"
        )

    # language bars
    parts.append('<text class="f mono in" style="animation-delay:.5s" x="44" y="150" fill="#5b6789" font-size="11.5" letter-spacing="2.4">TOP LANGUAGES</text>')
    bar_x, bar_w = 44, 792
    y = 166
    stacked_x = bar_x
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w}" height="12" rx="6" fill="#ffffff" fill-opacity=".06"/>')
    parts.append(f'<clipPath id="barclip"><rect x="{bar_x}" y="{y}" width="{bar_w}" height="12" rx="6"/></clipPath>')
    parts.append('<g clip-path="url(#barclip)">')
    for i, (name, size) in enumerate(top):
        w = bar_w * size / total
        parts.append(
            f'<rect class="bar" x="{stacked_x:.1f}" y="{y}" width="{max(w,2):.1f}" height="12" '
            f'fill="{colors[name]}" style="animation-delay:{0.35 + i * 0.09:.2f}s"/>'
        )
        stacked_x += w
    parts.append("</g>")

    # legend
    lx = bar_x
    for i, (name, size) in enumerate(top):
        pct = 100.0 * size / total
        label = f"{esc(name)} {pct:.1f}%"
        parts.append(
            f'<g class="f in" style="animation-delay:{0.6 + i * 0.08:.2f}s">'
            f'<circle cx="{lx + 5}" cy="{y + 44}" r="5" fill="{colors[name]}"/>'
            f'<text x="{lx + 18}" y="{y + 48}" fill="#a9b6d6" font-size="12.5">{label}</text>'
            f"</g>"
        )
        lx += 26 + int(7.0 * len(label))
    parts.append(f'<text class="f mono" x="836" y="{y + 48}" fill="#3f4a68" font-size="10.5" text-anchor="end">auto-generated daily</text>')
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("GH_TOKEN or GITHUB_TOKEN is required")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(fetch()))
    print(f"wrote {OUT}")
