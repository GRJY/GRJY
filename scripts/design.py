"""Shared design system for the profile SVG cards.

Tokens follow GitHub Primer so the cards read as part of the page rather than
as pasted-in graphics. Motion follows one rule: a single ~260ms ease-out entrance
with a short stagger. Nothing loops.
"""

W = 880

SANS = ('-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", '
        'Helvetica, Arial, sans-serif')
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'
EASE = "cubic-bezier(0.23, 1, 0.32, 1)"

BASE_CSS = f"""
  :root {{
    --canvas:  #ffffff;
    --surface: #f6f8fa;
    --line:    #d1d9e0;
    --fg:      #1f2328;
    --muted:   #59636e;
    --faint:   #818b98;
    --accent:  #0969da;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --canvas:  #0d1117;
      --surface: #151b23;
      --line:    #3d444d;
      --fg:      #f0f6fc;
      --muted:   #9198a1;
      --faint:   #656c76;
      --accent:  #4493f8;
    }}
  }}
  text {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .fg {{ fill: var(--fg); }}
  .mut {{ fill: var(--muted); }}
  .fnt {{ fill: var(--faint); }}
  .acc {{ fill: var(--accent); }}
  .surf {{ fill: var(--surface); }}
  .canvas {{ fill: var(--canvas); }}
  .line-f {{ fill: var(--line); }}
  .line-s {{ stroke: var(--line); }}
  .display {{ font-size: 42px; font-weight: 600; letter-spacing: -1.25px; }}
  .lead {{ font-size: 16.5px; font-weight: 500; letter-spacing: -0.2px; }}
  .body {{ font-size: 13px; }}
  .small {{ font-size: 11.5px; }}
  .title {{ font-size: 13.5px; font-weight: 600; letter-spacing: -0.1px; }}
  .metric {{ font-size: 30px; font-weight: 600; letter-spacing: -0.8px;
            font-variant-numeric: tabular-nums; }}
  .eyebrow {{ font-size: 10px; font-weight: 600; letter-spacing: 1.6px; }}
  .e {{ animation: e 260ms {EASE} both; transform-box: fill-box; }}
  @keyframes e {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .grow {{ animation: grow 520ms {EASE} both; transform-box: fill-box;
          transform-origin: left center; }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @media (prefers-reduced-motion: reduce) {{
    .e, .grow {{ animation: none; }}
  }}
"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def open_svg(h, label, extra_css=""):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}">',
        f'<style>{BASE_CSS}{extra_css}</style>',
        f'<rect width="{W}" height="{h}" class="canvas"/>',
    ]


def delay(ms):
    return f' style="animation-delay:{ms}ms"' if ms else ""


def txt(x, y, s, cls="body mut", anchor=None, d=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    dd = delay(d) if d is not None else ""
    return f'<text x="{x}" y="{y}" class="{cls}"{a}{dd}{extra}>{esc(s)}</text>'


def rule(x, y, w, d=None, opacity="1"):
    dd = delay(d) if d is not None else ""
    cls = "line-f e" if d is not None else "line-f"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="1" class="{cls}" '
            f'opacity="{opacity}"{dd}/>')


def eyebrow_row(x, y, label, width, d=0):
    """Small caps label followed by a hairline that runs to the right edge."""
    text_w = int(6.9 * len(label)) + 14
    return [
        f'<g class="e"{delay(d)}>',
        txt(x, y, label, cls="eyebrow fnt"),
        f'<rect x="{x + text_w}" y="{y - 4}" width="{max(width - text_w, 0)}" '
        f'height="1" class="line-f"/>',
        '</g>',
    ]
