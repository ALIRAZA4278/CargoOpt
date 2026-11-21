"""
ui.py - The look of CargoOpt (our own design), written in Python.

Each function here only builds a piece of the page (styles, truck drawing, timeline, ...)
from data that app.py gives it. There is NO Knapsack calculation in this file:
all calculations are in knapsack.py.
"""

import base64
from html import escape

FULL = 0.999999


def svg_image(svg, css_class="", alt=""):
    """Streamlit removes <svg> tags from HTML, so drawings are shown as an <img> holding the SVG."""
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{css_class}" alt="{escape(alt)}" src="data:image/svg+xml;base64,{data}">'
PALETTE = ["#0f766e", "#2563eb", "#7c3aed", "#db2777", "#ea580c", "#ca8a04",
           "#059669", "#0891b2", "#4f46e5", "#e11d48", "#65a30d", "#9333ea"]


def color_of(index):
    """Every package keeps the same colour everywhere (table, truck, timeline)."""
    return PALETTE[index % len(PALETTE)]


# ---------------------------------------------------------------------------
# Page styles (our design applied on top of Streamlit)
# ---------------------------------------------------------------------------
CSS = """
<style>
  /* ----- page frame ----- */
  header[data-testid="stHeader"] { display: none; }
  [data-testid="stMainBlockContainer"] { max-width: 1200px; padding: 0 16px 40px; }
  .stApp { background: #f5f6f8; }

  /* ----- cards: every container whose key starts with "card_" ----- */
  [class*="st-key-card_"] {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px 18px;
    box-shadow: 0 1px 3px rgba(16,24,40,.08), 0 1px 2px rgba(16,24,40,.04); gap: 12px;
  }
  .ch h2 { margin: 0; padding: 0; font-size: 16px; font-weight: 650; color: #111827; display: flex; align-items: center; gap: 8px; }
  .ch p { margin: 2px 0 0; font-size: 13px; color: #6b7280; }
  .count { font-size: 12px; font-weight: 600; color: #6b7280; background: #f8fafc; border: 1px solid #e5e7eb; padding: 0 8px; border-radius: 999px; line-height: 20px; }

  /* ----- app bar ----- */
  .appbar { display: flex; align-items: center; gap: 12px; padding: 14px 2px 16px; margin-bottom: 4px; border-bottom: 1px solid #e5e7eb; }
  .mark { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; color: #fff; flex: none;
          background: linear-gradient(135deg, #14b8a6, #0f766e); box-shadow: 0 2px 6px rgba(15,118,110,.35); }
  .brand b { display: block; font-size: 18px; line-height: 1.15; color: #111827; }
  .brand span { display: block; font-size: 12.5px; color: #6b7280; }
  .tagline { margin-left: 16px; padding-left: 16px; border-left: 1px solid #e5e7eb; font-size: 13px; color: #6b7280; }
  .status { margin-left: auto; display: inline-flex; align-items: center; gap: 7px; height: 30px; padding: 0 12px; border-radius: 999px;
            border: 1px solid #e5e7eb; background: #fff; font-size: 12.5px; font-weight: 600; color: #374151; white-space: nowrap; }
  .status i { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,.2); }
  @media (max-width: 760px) { .tagline { display: none; } }

  /* ----- strategy selector (segmented control) ----- */
  .st-key-strategy, .st-key-strategy [data-testid="stButtonGroup"] { width: 100% !important; }
  .st-key-strategy [role="radiogroup"] { display: grid !important; grid-template-columns: repeat(4, 1fr); gap: 4px; width: 100%;
       padding: 4px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 12px; }
  .st-key-strategy button { width: 100%; max-width: none; min-height: 58px; margin: 0 !important; border-radius: 9px !important;
       border: 0 !important; background: transparent !important; color: #6b7280 !important; }
  .st-key-strategy button[aria-checked="true"] { background: #fff !important; color: #0f766e !important;
       box-shadow: 0 1px 3px rgba(16,24,40,.12); outline: 1px solid #e5e7eb; }
  .st-key-strategy button * { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }
  .st-key-strategy button p { margin: 0; font-size: 12.5px; font-weight: 600; line-height: 1.3; text-align: center; }
  .st-key-strategy button strong { display: block; font-size: 16px; color: #111827; margin-top: 2px; }
  @media (max-width: 640px) { .st-key-strategy [role="radiogroup"] { grid-template-columns: repeat(2, 1fr); } }

  .rule { margin: 0; font-size: 13px; color: #6b7280; }

  /* ----- stats ----- */
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid #e5e7eb; border-radius: 12px; background: #f8fafc; }
  .stat { padding: 10px 12px; min-width: 0; }
  .stat + .stat { border-left: 1px solid #e5e7eb; }
  .stat span { display: block; font-size: 11.5px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .04em; }
  .stat b { display: block; margin-top: 2px; font-size: 24px; font-weight: 700; letter-spacing: -.02em; color: #111827; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
  .stat b small { font-size: 13px; font-weight: 500; color: #6b7280; letter-spacing: 0; }
  .stat.accent b { color: #0f766e; }
  .delta { display: block; width: fit-content; margin-top: 3px; font-size: 12px; font-weight: 600; padding: 0 7px; border-radius: 99px; line-height: 19px; }
  .delta.up { color: #15803d; background: #f0fdf4; } .delta.down { color: #dc2626; background: #fef2f2; }
  @media (max-width: 640px) { .stat b { font-size: 19px; } }

  /* ----- truck ----- */
  .truck { width: 100%; height: auto; display: block; margin-top: 4px; }
  .mark img { width: 19px; height: 19px; }
  .tr-body { fill: #f1f5f9; } .tr-line { stroke: #334155; } .tr-rib { stroke: #334155; stroke-opacity: .12; }
  .tr-dark { fill: #334155; } .tr-cab { fill: #0f766e; } .tr-win { fill: #ccfbf1; }
  .tr-tire { fill: #1f2937; } .tr-hub { fill: #cbd5e1; } .tr-shadow { fill: #111827; opacity: .08; }
  .seg-r { transform-box: fill-box; transform-origin: left; animation: grow .45s cubic-bezier(.2,.8,.2,1) both; }
  @keyframes grow { from { transform: scaleX(0); } }
  .seg-n { fill: #fff; font-size: 20px; font-weight: 700; text-anchor: middle; dominant-baseline: central; font-family: sans-serif; }
  .scale { display: flex; justify-content: space-between; font-size: 12px; color: #6b7280; margin: 0 24.5% 0 1.4%; }

  /* ----- loading sequence ----- */
  .sub-head { display: flex; align-items: baseline; justify-content: space-between; margin: 14px 0 2px; }
  .sub-head h3 { margin: 0; padding: 0; font-size: 14px; font-weight: 650; color: #111827; }
  .sub-head span { font-size: 12.5px; color: #6b7280; }
  .timeline { list-style: none; margin: 0; padding: 0; }
  .timeline li { display: grid; grid-template-columns: 28px minmax(0, 1fr) auto; gap: 12px; padding: 10px 0; align-items: start; margin: 0; }
  .timeline li + li { border-top: 1px dashed #e5e7eb; }
  .node { width: 28px; height: 28px; border-radius: 8px; display: grid; place-items: center; color: #fff; font-size: 12.5px; font-weight: 700; }
  .t-main b { display: block; font-size: 14px; font-weight: 600; color: #111827; overflow-wrap: anywhere; }
  .t-main > span { display: block; font-size: 12.5px; color: #6b7280; }
  .t-gain { font-weight: 700; font-size: 14px; color: #15803d; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .tag { display: inline-block; font-size: 11px; font-weight: 600; padding: 0 6px; border-radius: 4px; line-height: 17px; margin-left: 6px;
         background: #f0fdfa; color: #0f766e; vertical-align: 1px; }

  /* ----- comparison ----- */
  .cmp { display: grid; gap: 14px; }
  .cmp-row .top { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
  .cmp-row b { font-size: 14px; font-weight: 600; color: #111827; }
  .cmp-row .val { font-weight: 700; color: #111827; font-variant-numeric: tabular-nums; }
  .cmp-row .meta { display: flex; justify-content: space-between; gap: 10px; font-size: 12.5px; color: #6b7280; margin-top: 6px; }
  .bar { height: 8px; border-radius: 99px; background: #f8fafc; border: 1px solid #e5e7eb; overflow: hidden; margin-top: 6px; }
  .bar i { display: block; height: 100%; border-radius: 99px; background: #d1d5db; }
  .cmp-row.best .bar i { background: linear-gradient(90deg, #0d9488, #0f766e); }
  .badge { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; padding: 1px 6px; border-radius: 4px; margin-left: 6px;
           color: #15803d; background: #f0fdf4; vertical-align: 1px; }
  .neg { color: #dc2626; font-variant-numeric: tabular-nums; }

  /* ----- callouts, footer, empty states ----- */
  .callout { display: flex; gap: 10px; align-items: flex-start; padding: 10px 12px; border-radius: 10px; font-size: 13px; color: #374151;
             background: #f0fdfa; border: 1px solid #ccebe7; }
  .callout svg { flex: none; color: #0f766e; margin-top: 1px; }
  .callout.bad { background: #fef2f2; border-color: #fbd5d5; } .callout.bad svg { color: #dc2626; }
  .loadbar { display: flex; flex-wrap: wrap; gap: 6px 16px; justify-content: space-between; font-size: 13.5px; color: #6b7280;
             padding-top: 10px; border-top: 1px solid #e5e7eb; }
  .loadbar b { color: #111827; font-variant-numeric: tabular-nums; }
  .loadbar .over { color: #dc2626; font-weight: 600; }
  .empty { padding: 24px 12px; text-align: center; color: #6b7280; font-size: 14px; }
  .empty b { display: block; color: #111827; font-size: 15px; margin-bottom: 2px; }
  .foot { text-align: center; font-size: 12.5px; color: #6b7280; padding: 8px 0 0; }

  /* ----- Streamlit widgets in our style ----- */
  [class*="st-key-card_"] [data-testid="stFormSubmitButton"] button, .st-key-card_plan [data-testid="stDownloadButton"] button { border-radius: 10px; }
  [data-testid="stForm"] { border: 0; padding: 0; }
  [data-testid="stExpander"] details { border-radius: 14px; background: #fff; border: 1px solid #e5e7eb; }
</style>
"""

_INFO_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/></svg>')


# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------
def app_bar():
    truck_icon = ('<svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" '
                  'stroke-linecap="round" stroke-linejoin="round"><path d="M1 3h15v13H1zM16 8h4l3 3v5h-7zM5.5 16a2.5 2.5 0 1 0 0 '
                  '5 2.5 2.5 0 0 0 0-5zM18.5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z"/></svg>')
    return (f'<div class="appbar"><span class="mark">{svg_image(truck_icon, alt="CargoOpt")}</span>'
            '<div class="brand"><b>CargoOpt</b><span>Truck load optimizer</span></div>'
            '<div class="tagline">Fractional Knapsack &middot; Greedy strategies</div>'
            '<span class="status"><i></i>knapsack.py</span></div>')


def card_head(title, subtitle, count=None):
    badge = f'<span class="count">{count}</span>' if count is not None else ""
    return f'<div class="ch"><h2>{escape(title)} {badge}</h2><p>{escape(subtitle)}</p></div>'


def callout(text_html, bad=False):
    return f'<div class="callout{" bad" if bad else ""}">{_INFO_ICON}<span>{text_html}</span></div>'


def empty(title, text):
    return f'<div class="empty"><b>{escape(title)}</b>{escape(text)}</div>'


def stats(profit_text, delta_text, delta_good, loaded_text, capacity_text, util_text):
    delta = f'<span class="delta {"up" if delta_good else "down"}">{escape(delta_text)}</span>'
    return (f'<div class="stats">'
            f'<div class="stat accent"><span>Profit</span><b>{escape(profit_text)}</b>{delta}</div>'
            f'<div class="stat"><span>Loaded</span><b>{escape(loaded_text)}<small> / {escape(capacity_text)}</small></b></div>'
            f'<div class="stat"><span>Utilization</span><b>{escape(util_text)}</b></div></div>')


# ---------------------------------------------------------------------------
# The truck drawing (scales to any screen)
# ---------------------------------------------------------------------------
def truck(steps, capacity, capacity_text):
    """Each step of the plan becomes a coloured block; its width = weight / capacity."""
    X, Y, W, H = 10, 18, 530, 122
    x = X
    segs = []
    for s in steps:
        w = s["weight_taken"] / capacity * W
        c = color_of(s["item"])
        segs.append(f'<rect class="seg-r" x="{x:.2f}" y="{Y}" width="{w:.2f}" height="{H}" fill="{c}"/>')
        if s["fraction"] < FULL:   # partly loaded package: striped
            segs.append(f'<rect class="seg-r" x="{x:.2f}" y="{Y}" width="{w:.2f}" height="{H}" fill="url(#hatch)"/>')
        segs.append(f'<rect x="{x:.2f}" y="{Y}" width="{w:.2f}" height="{H}" fill="url(#shine)"/>')
        segs.append(f'<line x1="{x + w:.2f}" x2="{x + w:.2f}" y1="{Y}" y2="{Y + H}" stroke="#fff" stroke-opacity=".75" stroke-width="2"/>')
        if w > 28:
            segs.append(f'<text class="seg-n" x="{x + w / 2:.2f}" y="{Y + H / 2}">{s["item"] + 1}</text>')
        x += w

    ribs = "".join(f'<line class="tr-rib" x1="{rx}" x2="{rx}" y1="{Y + 6}" y2="{Y + H - 6}" stroke-width="2"/>'
                   for rx in range(X + 44, X + W, 44))

    def wheel(cx):
        return (f'<circle class="tr-tire" cx="{cx}" cy="162" r="21"/><circle class="tr-hub" cx="{cx}" cy="162" r="9"/>'
                f'<circle class="tr-tire" cx="{cx}" cy="162" r="3"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 196">
  <style>
    .tr-body {{ fill: #f1f5f9; }} .tr-line {{ stroke: #334155; }} .tr-rib {{ stroke: #334155; stroke-opacity: .12; }}
    .tr-dark {{ fill: #334155; }} .tr-cab {{ fill: #0f766e; }} .tr-win {{ fill: #ccfbf1; }}
    .tr-tire {{ fill: #1f2937; }} .tr-hub {{ fill: #cbd5e1; }} .tr-shadow {{ fill: #111827; opacity: .08; }}
    .seg-r {{ transform-box: fill-box; transform-origin: left; animation: grow .45s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} }}
    .seg-n {{ fill: #fff; font: 700 20px system-ui, sans-serif; text-anchor: middle; dominant-baseline: central; }}
  </style>
  <defs>
    <clipPath id="bay"><rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"/></clipPath>
    <pattern id="hatch" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="12" fill="rgba(255,255,255,.38)"/></pattern>
    <linearGradient id="shine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient>
  </defs>
  <ellipse class="tr-shadow" cx="360" cy="186" rx="350" ry="7"/>
  <rect class="tr-body" x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"/>
  <g clip-path="url(#bay)">{ribs}{"".join(segs)}</g>
  <rect class="tr-line" x="{X}" y="{Y}" width="{W}" height="{H}" rx="8" fill="none" stroke-width="3"/>
  <rect class="tr-dark" x="10" y="140" width="696" height="10" rx="3"/>
  <path class="tr-cab" d="M550 54 h66 q10 0 17 7 l52 49 q9 8 9 20 v20 h-144 z"/>
  <path class="tr-win" d="M622 66 l44 42 h-44 z"/>
  <rect class="tr-dark" x="562" y="66" width="44" height="40" rx="5" opacity=".18"/>
  <rect x="684" y="118" width="10" height="10" rx="2" fill="#fde68a"/>
  <rect class="tr-dark" x="688" y="140" width="18" height="12" rx="3"/>
  {wheel(96)}{wheel(176)}{wheel(642)}
</svg>"""
    picture = svg_image(svg, "truck", alt=f"Truck with {len(steps)} packages loaded")
    return picture + f'<div class="scale"><span>0</span><span>{escape(capacity_text)}</span></div>'


# ---------------------------------------------------------------------------
# Loading sequence (timeline) and comparison
# ---------------------------------------------------------------------------
def timeline(rows, loaded_count, total_count):
    """rows: dicts with item, name, partial, detail, gain (all text prepared by app.py)."""
    items = "".join(
        f'<li><span class="node" style="background:{color_of(r["item"])}">{r["item"] + 1}</span>'
        f'<div class="t-main"><b>{escape(r["name"])}{"<span class=tag>Partial</span>" if r["partial"] else ""}</b>'
        f'<span>{escape(r["detail"])}</span></div><span class="t-gain">+{escape(r["gain"])}</span></li>'
        for r in rows)
    return (f'<div class="sub-head"><h3>Loading sequence</h3><span>{loaded_count} of {total_count} packages</span></div>'
            f'<ol class="timeline">{items}</ol>')


def comparison(rows):
    """rows: dicts with name, desc, value, pct, best, gap (text or None)."""
    out = []
    for r in rows:
        badge = '<span class="badge">Optimal</span>' if r["best"] else ""
        gap = f'<span class="neg">&minus;{escape(r["gap"])}</span> vs best' if r["gap"] else "Highest profit"
        out.append(f'<div class="cmp-row{" best" if r["best"] else ""}">'
                   f'<div class="top"><b>{escape(r["name"])}{badge}</b><span class="val">{escape(r["value"])}</span></div>'
                   f'<div class="bar"><i style="width:{r["pct"]:.1f}%"></i></div>'
                   f'<div class="meta"><span>{escape(r["desc"])}</span><span>{gap}</span></div></div>')
    return f'<div class="cmp">{"".join(out)}</div>'


def load_footer(count, weight_text, capacity_text, profit_text, free_text, over=False):
    left = (f'Your load: <b>{count}</b> package{"" if count == 1 else "s"} &middot; '
            f'<b>{escape(weight_text)}</b> of {escape(capacity_text)}')
    right = ('<span class="over">Over capacity: untick some packages</span>' if over
             else f'Profit <b>{escape(profit_text)}</b> &middot; Free <b>{escape(free_text)}</b>')
    return f'<div class="loadbar"><span>{left}</span><span>{right}</span></div>'


def footer():
    return '<div class="foot">CargoOpt &middot; DAA project &middot; All calculations by <b>knapsack.py</b> (Python)</div>'
