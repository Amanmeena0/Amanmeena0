#!/usr/bin/env python3
"""make_info_card.py – neofetch-style info panel as animated SVG."""
import os

# ── CONFIG ── edit these ──────────────────────────────────────────
HOST = "aman@earth"
ROWS = [
    ("os",        "AI Engineer · Delhi, India"),
    ("uptime",    "~3 yrs building AI products"),
    ("shell",     "Python · TypeScript · C++"),
    ("wm",        "PyTorch · TensorFlow · HuggingFace"),
    ("editor",    "VS Code · Neovim · Cursor"),
    ("cloud",     "AWS · GCP · Docker · K8s"),
    ("frontend",  "React · Next.js · TailwindCSS"),
    ("backend",   "FastAPI · Node.js · PostgreSQL"),
    ("interests", "LLMs · Computer Vision · MLOps"),
    ("fun",       "Hala Madrid · F1 · Anime"),
]
W = 490
H = 420
OUT = "info-card.svg"
BG_COLOR   = "#0d1117"
TEXT_COLOR = "#c9d1d9"
KEY_COLOR  = "#58a6ff"
HOST_COLOR = "#58a6ff"
FONT_SIZE  = 13
LINE_H     = 24
ROW_DUR    = 0.06
STAGGER    = 0.04
# ── END CONFIG ────────────────────────────────────────────────────

def main():
    static = os.environ.get('STATIC', '') == '1'
    
    lines = []
    # Header: host line + separator
    lines.append((HOST, None, True))  # host line
    lines.append(("-" * len(HOST), None, False))  # separator
    for key, val in ROWS:
        lines.append((key, val, False))
    # Blank line before palette
    lines.append((None, None, False))
    
    total_lines = len(lines)
    svg_h = max(H, 60 + total_lines * LINE_H + 40)
    
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {svg_h}" width="{W}" height="{svg_h}">')
    parts.append(f'<rect width="100%" height="100%" fill="{BG_COLOR}" rx="6"/>')
    
    # Terminal dots
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        cx = 20 + i * 20
        parts.append(f'<circle cx="{cx}" cy="16" r="6" fill="{color}"/>')
    
    # Style
    parts.append('<style>')
    parts.append(f'text {{ font-family: "SFMono-Regular","Cascadia Code","Fira Code","Menlo",monospace; font-size: {FONT_SIZE}px; fill: {TEXT_COLOR}; }}')
    if not static:
        for i in range(total_lines + 1):  # +1 for palette
            delay = i * STAGGER
            parts.append(f'.l{i} {{ opacity: 0; animation: type {ROW_DUR}s {delay:.3f}s forwards; }}')
        parts.append('@keyframes type { from { opacity: 0; } to { opacity: 1; } }')
    parts.append('</style>')
    
    y = 50
    for idx, (left, right, is_host) in enumerate(lines):
        if left is None:
            y += LINE_H
            continue
        cls = f' class="l{idx}"' if not static else ''
        if is_host:
            parts.append(f'<text x="20" y="{y}"{cls}><tspan fill="{HOST_COLOR}">{left}</tspan></text>')
        elif right is None:
            parts.append(f'<text x="20" y="{y}"{cls}><tspan fill="{TEXT_COLOR}">{left}</tspan></text>')
        else:
            parts.append(f'<text x="20" y="{y}"{cls}><tspan fill="{KEY_COLOR}">{left}</tspan><tspan fill="{TEXT_COLOR}"> ~ {right}</tspan></text>')
        y += LINE_H
    
    # Color palette blocks
    palette_y = y + 5
    colors_dark = ["#282c34", "#e06c75", "#98c379", "#e5c07b", "#61afef", "#c678dd", "#56b6c2", "#abb2bf"]
    colors_bright = ["#5c6370", "#be5046", "#7ec16e", "#d19a66", "#4e88ff", "#a475cf", "#48a8b5", "#ffffff"]
    bw = 22
    cls_attr = f' class="l{total_lines}"' if not static else ''
    for i, c in enumerate(colors_dark):
        x = 20 + i * (bw + 4)
        parts.append(f'<rect x="{x}" y="{palette_y}" width="{bw}" height="{bw}" rx="3" fill="{c}"{cls_attr}/>')
    for i, c in enumerate(colors_bright):
        x = 20 + i * (bw + 4)
        parts.append(f'<rect x="{x}" y="{palette_y + bw + 4}" width="{bw}" height="{bw}" rx="3" fill="{c}"{cls_attr}/>')
    
    parts.append('</svg>')
    svg = '\n'.join(parts)
    
    with open(OUT, 'w') as f:
        f.write(svg)
    print(f"[info] Wrote {OUT} ({W}x{svg_h})")

if __name__ == '__main__':
    main()
