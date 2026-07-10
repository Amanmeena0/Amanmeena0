#!/usr/bin/env python3
"""make_ascii_svg.py – photo → typing monochrome ASCII portrait (SVG+SMIL)."""
import os
import math
from PIL import Image

# ── CONFIG ────────────────────────────────────────────────────────
SRC        = "source-prepped.png"   # prepped grayscale portrait
OUT        = "avi-ascii.svg"        # output SVG
COLS       = 80                     # ASCII columns
CONTRAST   = 1.6                    # >1 = punchier
GAMMA      = 0.7                    # <1 = brighter mids
WHITE_FLOOR = 240                   # pixels brighter than this → space
CHAR_W     = 6.8                    # px per character cell
CHAR_H     = 13                     # px per row
FONT_SIZE  = 11                     # monospace font size
FG_COLOR   = "#c9d1d9"              # light gray (GitHub dark theme)
BG_COLOR   = "#0d1117"              # dark background
ROW_DUR    = 0.08                   # seconds per row reveal
STAGGER    = 0.03                   # delay between rows
CHARS      = '@%#*+=-:. '           # dark → light
# ── END CONFIG ────────────────────────────────────────────────────

def img_to_ascii(path, cols):
    img = Image.open(path).convert('L')
    w, h = img.size
    cell_w = w / cols
    cell_h = cell_w * (CHAR_H / CHAR_W)
    rows = int(h / cell_h)
    img = img.resize((cols, rows), Image.LANCZOS)
    
    pixels = list(img.getdata())
    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            v = pixels[r * cols + c]
            # Apply contrast
            v = int(((v / 255.0 - 0.5) * CONTRAST + 0.5) * 255)
            v = max(0, min(255, v))
            # Apply gamma
            v = int(255 * ((v / 255.0) ** GAMMA))
            # White floor
            if v >= WHITE_FLOOR:
                row_chars.append(' ')
            else:
                idx = int(v / 255.0 * (len(CHARS) - 1))
                row_chars.append(CHARS[idx])
        lines.append(''.join(row_chars))
    return lines

def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def make_svg(lines):
    static = os.environ.get('STATIC', '') == '1'
    nrows = len(lines)
    svg_w = int(COLS * CHAR_W) + 20
    svg_h = int(nrows * CHAR_H) + 20
    
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    parts.append(f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>')
    
    # Style block
    parts.append('<style>')
    parts.append(f'text {{ font-family: "SFMono-Regular","Cascadia Code","Fira Code","Menlo",monospace; font-size: {FONT_SIZE}px; fill: {FG_COLOR}; white-space: pre; }}')
    if not static:
        for i in range(nrows):
            delay = i * STAGGER
            parts.append(f'.r{i} {{ opacity: 0; animation: reveal {ROW_DUR}s {delay:.3f}s forwards; }}')
        parts.append('@keyframes reveal { from { opacity: 0; } to { opacity: 1; } }')
    parts.append('</style>')
    
    # Text rows
    for i, line in enumerate(lines):
        y = 14 + i * CHAR_H
        cls = f' class="r{i}"' if not static else ''
        escaped = escape_xml(line)
        parts.append(f'<text x="10" y="{y}"{cls}>{escaped}</text>')
    
    parts.append('</svg>')
    return '\n'.join(parts)

def main():
    print(f"[ascii] Converting {SRC} to ASCII...")
    lines = img_to_ascii(SRC, COLS)
    print(f"[ascii] Generated {len(lines)} rows x {COLS} cols")
    svg = make_svg(lines)
    with open(OUT, 'w') as f:
        f.write(svg)
    static = os.environ.get('STATIC', '') == '1'
    mode = 'STATIC' if static else 'ANIMATED'
    print(f"[ascii] Wrote {OUT} ({mode})")

if __name__ == '__main__':
    main()
