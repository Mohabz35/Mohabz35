#!/usr/bin/env python3
"""
Renders an animated GitHub contribution heatmap as a standalone SVG.
Cells pop in diagonally with CSS animations, compatible with GitHub <img> tags.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "contrib-heatmap.svg")

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
INK = "#e6edf3"
MUTED = "#7d8590"

# Dark theme contribution levels
PALETTE = [
    "#161b22",  # 0: empty
    "#0e4429",  # 1: 1-3
    "#006d32",  # 2: 4-9
    "#26a641",  # 3: 10-19
    "#39d353",  # 4: 20+
]


def level_for(c):
    if c <= 0:
        return 0
    if c <= 3:
        return 1
    if c <= 9:
        return 2
    if c <= 19:
        return 3
    return 4


def render():
    if not os.path.exists(SRC):
        print(f"Data file not found at {SRC}. Run fetch_contributions.py first.", file=sys.stderr)
        return

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    if not days:
        print("No days in contributions data.", file=sys.stderr)
        return

    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # 0 = Sunday

    cell, step = 11, 14
    gx, gy = 36, 75
    cells, months, seen_months = [], [], set()

    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen_months and row == 0:
            seen_months.add((date.year, date.month))
            months.append((col, date.strftime("%b")))

        c = day["count"]
        delay = 0.2 + col * 0.02 + row * 0.025
        lvl = level_for(c)
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="2.5" fill="{PALETTE[lvl]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )

    ncols = (len(days) + lead + 6) // 7
    total_w = gx * 2 + ncols * step
    total_h = gy + 7 * step + 45
    right = gx + ncols * step - 3

    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 18}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="10" fill="{MUTED}">{m}</text>'
        for col, m in months if col < ncols - 5
    )

    legend_x = right - len(PALETTE) * 15
    legend = "".join(
        f'<rect x="{legend_x + i * 15}" y="{gy + 7 * step + 8}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    user = data.get("username", "developer")
    total_contribs = data.get("total_contributions", 0)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', ui-monospace, SFMono-Regular, Menlo, monospace">
  <style>
    @keyframes pop {{
      0% {{ opacity: 0; transform: scale(0.3); }}
      70% {{ opacity: 1; transform: scale(1.15); }}
      100% {{ opacity: 1; transform: none; }}
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: none; }}
    }}
    .p {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      animation: pop 0.35s ease-out both;
    }}
    .f {{
      opacity: 0;
      animation: fadeIn 0.6s ease-out both;
    }}
    @media (prefers-reduced-motion: reduce) {{
      .p, .f {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
    }}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG2}"/>
      <stop offset="1" stop-color="{BG}"/>
    </linearGradient>
  </defs>
  <rect width="{total_w}" height="{total_h}" rx="14" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{total_w - 1}" height="{total_h - 1}" rx="14" fill="none" stroke="{FRAME}"/>

  <text class="f" style="animation-delay:0.1s" x="{gx}" y="42" font-size="18" font-weight="600" fill="{INK}">
    Contributions in the last year: <tspan fill="{PALETTE[4]}">{total_contribs:,}</tspan>
  </text>
  <text class="f" style="animation-delay:0.2s" x="{right}" y="42" text-anchor="end" font-size="11" letter-spacing="1" fill="{MUTED}">
    LIVE REFRESH • @{user}
  </text>

  {''.join(cells)}

  <g class="f" style="animation-delay:1.2s">
    {labels}
    <text x="{legend_x - 8}" y="{gy + 7 * step + 18}" text-anchor="end" font-size="10" fill="{MUTED}">Less</text>
    {legend}
    <text x="{legend_x + len(PALETTE) * 15 + 4}" y="{gy + 7 * step + 18}" font-size="10" fill="{MUTED}">More</text>
  </g>
</svg>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {OUT}: {total_w}x{total_h} SVG.")


if __name__ == "__main__":
    render()
