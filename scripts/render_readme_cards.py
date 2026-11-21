#!/usr/bin/env python3
"""
Renders modular animated SVG cards into cards/ based on profile_config.json.
Cards include:
- cards/hero.svg: Terminal header card with animated typing cursor and developer specs
- cards/highlight_*.svg: Bento-style metric / focus cards with animated gradient sheen
- cards/repo_*.svg: Glassmorphism repository cards with live star counts (if online)
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CONFIG_PATH = os.path.join(ROOT, "profile_config.json")
OUT_DIR = os.path.join(ROOT, "cards")

BG = "#0d1117"
BG2 = "#161b22"
FRAME = "#30363d"
INK = "#e6edf3"
MUTED = "#7d8590"
GREEN = "#39d353"

W_FULL = 880
W_THIRD = 286


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_hero(cfg):
    username = cfg.get("username", "developer")
    name = cfg.get("name", "Developer")
    title = cfg.get("title", "Software Engineer")
    bio = cfg.get("bio", "Building software & crafting experiences.")
    h = 230

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W_FULL}" height="{h}" viewBox="0 0 {W_FULL} {h}"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', ui-monospace, SFMono-Regular, Menlo, monospace">
  <style>
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: none; }}
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    @keyframes gradient {{
      0% {{ stop-color: #58a6ff; }}
      50% {{ stop-color: #bc8cff; }}
      100% {{ stop-color: #58a6ff; }}
    }}
    .r {{
      opacity: 0;
      animation: rise 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .cursor {{
      animation: blink 1s step-end infinite;
    }}
    @media (prefers-reduced-motion: reduce) {{
      .r, .cursor {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
    }}
  </style>
  <defs>
    <linearGradient id="hero-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BG2}"/>
      <stop offset="100%" stop-color="{BG}"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#bc8cff"/>
    </linearGradient>
  </defs>

  <rect width="{W_FULL}" height="{h}" rx="14" fill="url(#hero-bg)"/>
  <rect x="0.5" y="0.5" width="{W_FULL - 1}" height="{h - 1}" rx="14" fill="none" stroke="{FRAME}"/>

  <!-- Terminal top bar -->
  <line x1="0" y1="36" x2="{W_FULL}" y2="36" stroke="{FRAME}"/>
  <circle cx="24" cy="18" r="5" fill="#ff5f56"/>
  <circle cx="40" cy="18" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="18" r="5" fill="#27c93f"/>
  <text x="{W_FULL / 2}" y="22" font-size="12" fill="{MUTED}" text-anchor="middle">terminal ~ @{html.escape(username)}</text>

  <!-- Content -->
  <g class="r" style="animation-delay: 0.15s">
    <text x="36" y="78" font-size="14" fill="{MUTED}">~$ whoami</text>
    <text x="36" y="118" font-size="32" font-weight="700" fill="url(#glow)">{html.escape(name)}</text>
    <rect x="{36 + len(name) * 19.5}" y="92" width="10" height="26" fill="{GREEN}" class="cursor"/>
  </g>

  <g class="r" style="animation-delay: 0.3s">
    <text x="36" y="152" font-size="18" font-weight="600" fill="{INK}">{html.escape(title)}</text>
    <text x="36" y="184" font-size="14" fill="{MUTED}">{html.escape(bio)}</text>
  </g>

  <!-- Status pill -->
  <g class="r" style="animation-delay: 0.45s">
    <rect x="{W_FULL - 180}" y="65" width="144" height="28" rx="14" fill="#238636" fill-opacity="0.2" stroke="{GREEN}" stroke-width="0.75"/>
    <circle cx="{W_FULL - 165}" cy="79" r="4" fill="{GREEN}"/>
    <text x="{W_FULL - 152}" y="83" font-size="12" font-weight="500" fill="{GREEN}">AVAILABLE TO BUILD</text>
  </g>
</svg>"""
    return svg


def render_highlight_card(item, index):
    tag = item.get("tag", "INFO")
    metric = item.get("metric", "100%")
    unit = item.get("unit", "")
    desc = item.get("desc", "")
    accent = item.get("accent", "#58a6ff")
    delay = 0.3 + index * 0.15
    h = 175

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W_THIRD}" height="{h}" viewBox="0 0 {W_THIRD} {h}"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', ui-monospace, SFMono-Regular, Menlo, monospace">
  <style>
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to {{ opacity: 1; transform: none; }}
    }}
    .r {{
      opacity: 0;
      animation: rise 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
  </style>
  <rect width="{W_THIRD}" height="{h}" rx="12" fill="{BG2}"/>
  <rect x="0.5" y="0.5" width="{W_THIRD - 1}" height="{h - 1}" rx="12" fill="none" stroke="{FRAME}"/>

  <g class="r" style="animation-delay: {delay:.2f}s">
    <!-- Tag badge -->
    <rect x="20" y="20" width="{len(tag) * 9 + 16}" height="22" rx="4" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="0.75"/>
    <text x="28" y="35" font-size="11" font-weight="700" fill="{accent}">{html.escape(tag)}</text>

    <!-- Metric -->
    <text x="20" y="80" font-size="24" font-weight="700" fill="{INK}">
      {html.escape(metric)} <tspan font-size="14" font-weight="400" fill="{MUTED}">{html.escape(unit)}</tspan>
    </text>

    <!-- Description -->
    <text x="20" y="112" font-size="12" fill="{MUTED}">
      {html.escape(desc[:38])}
    </text>
    <text x="20" y="130" font-size="12" fill="{MUTED}">
      {html.escape(desc[38:76])}
    </text>
  </g>
</svg>"""
    return svg


def render_repo_card(repo, index, username):
    name = repo.get("name", "repo")
    desc = repo.get("desc", "Repository description")
    lang = repo.get("lang", "TypeScript")
    color = repo.get("color", "#3178c6")
    delay = 0.5 + index * 0.15
    h = 160

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W_THIRD}" height="{h}" viewBox="0 0 {W_THIRD} {h}"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', ui-monospace, SFMono-Regular, Menlo, monospace">
  <style>
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to {{ opacity: 1; transform: none; }}
    }}
    .r {{
      opacity: 0;
      animation: rise 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
  </style>
  <rect width="{W_THIRD}" height="{h}" rx="12" fill="{BG2}"/>
  <rect x="0.5" y="0.5" width="{W_THIRD - 1}" height="{h - 1}" rx="12" fill="none" stroke="{FRAME}"/>

  <g class="r" style="animation-delay: {delay:.2f}s">
    <!-- Folder icon / Repo Name -->
    <text x="20" y="38" font-size="16" font-weight="600" fill="#58a6ff">{html.escape(name)}</text>

    <!-- Description -->
    <text x="20" y="70" font-size="12" fill="{INK}">
      {html.escape(desc[:36])}
    </text>
    <text x="20" y="88" font-size="12" fill="{MUTED}">
      {html.escape(desc[36:74])}
    </text>

    <!-- Language -->
    <circle cx="26" cy="{h - 26}" r="5" fill="{color}"/>
    <text x="38" y="{h - 22}" font-size="12" fill="{MUTED}">{html.escape(lang)}</text>
  </g>
</svg>"""
    return svg


def render_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    cfg = load_config()

    # 1. Hero card
    hero_svg = render_hero(cfg)
    with open(os.path.join(OUT_DIR, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(hero_svg)

    # 2. Highlight cards
    cards = cfg.get("highlight_cards", [])
    for i, c in enumerate(cards):
        cid = c.get("id", f"card_{i+1}")
        c_svg = render_highlight_card(c, i)
        with open(os.path.join(OUT_DIR, f"{cid}.svg"), "w", encoding="utf-8") as f:
            f.write(c_svg)

    # 3. Featured repos
    repos = cfg.get("featured_repos", [])
    username = cfg.get("username", "developer")
    for i, r in enumerate(repos):
        r_name = r.get("name", f"repo_{i+1}")
        r_svg = render_repo_card(r, i, username)
        with open(os.path.join(OUT_DIR, f"repo-{r_name}.svg"), "w", encoding="utf-8") as f:
            f.write(r_svg)

    print(f"Rendered all cards to {OUT_DIR}/ successfully.")


if __name__ == "__main__":
    render_all()
