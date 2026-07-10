#!/usr/bin/env python3
"""render_heatmap_svg.py – contribution data → animated heatmap SVG."""
import json
import os
from datetime import datetime, timedelta

# ── CONFIG ────────────────────────────────────────────────────────
DATA_FILE  = "data/contributions.json"
OUT        = "contrib-heatmap.svg"
BOX_SIZE   = 11
BOX_GAP    = 3
BG_COLOR   = "#0d1117"
LEVELS     = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}
TEXT_COLOR = "#8b949e"
WEEKS      = 52
CELL_DELAY = 0.008   # seconds between cell reveals
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_LABELS = ["Mon","Wed","Fri"]
# ── END CONFIG ────────────────────────────────────────────────────

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def render_svg(data):
    days = data["days"]
    stats = data["stats"]
    
    # Build a date->level map
    day_map = {d["date"]: d["level"] for d in days}
    
    # Calculate grid: 52 weeks x 7 days, ending at the most recent date
    if days:
        sorted_dates = sorted(d["date"] for d in days)
        end_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
    else:
        end_date = datetime.utcnow()
    
    # Align to end of week (Saturday)
    while end_date.weekday() != 5:  # Saturday
        end_date += timedelta(days=1)
    
    start_date = end_date - timedelta(weeks=WEEKS) + timedelta(days=1)
    # Align to Sunday
    while start_date.weekday() != 6:
        start_date -= timedelta(days=1)
    
    # Build grid
    grid = []  # list of (week, day, date_str, level)
    current = start_date
    week = 0
    while current <= end_date:
        dow = current.weekday()  # 0=Mon ... 6=Sun
        # GitHub layout: Sun=0, Mon=1, ... Sat=6
        gh_dow = (dow + 1) % 7
        date_str = current.strftime("%Y-%m-%d")
        level = day_map.get(date_str, 0)
        grid.append((week, gh_dow, date_str, level))
        if gh_dow == 6:  # Saturday = end of week column
            week += 1
        current += timedelta(days=1)
    
    # SVG dimensions
    left_margin = 35
    top_margin = 25
    svg_w = left_margin + WEEKS * (BOX_SIZE + BOX_GAP) + 80
    grid_h = 7 * (BOX_SIZE + BOX_GAP)
    stats_y = top_margin + grid_h + 30
    legend_y = stats_y + 25
    svg_h = legend_y + 30
    
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    parts.append(f'<rect width="100%" height="100%" fill="{BG_COLOR}" rx="6"/>')
    
    # Style
    parts.append('<style>')
    parts.append(f'text {{ font-family: -apple-system,"Segoe UI",Helvetica,Arial,sans-serif; font-size: 10px; fill: {TEXT_COLOR}; }}')
    parts.append('.cell { opacity: 0; animation: pop 0.15s forwards; }')
    parts.append('@keyframes pop { from { opacity: 0; transform: scale(0); } to { opacity: 1; transform: scale(1); } }')
    parts.append('.stat-label { font-size: 11px; fill: #8b949e; }')
    parts.append('.stat-value { font-size: 13px; fill: #c9d1d9; font-weight: 600; }')
    parts.append('</style>')
    
    # Day labels (Mon, Wed, Fri)
    for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        y = top_margin + row * (BOX_SIZE + BOX_GAP) + BOX_SIZE - 2
        parts.append(f'<text x="2" y="{y}" font-size="9">{label}</text>')
    
    # Month labels
    month_positions = {}
    for (w, d, date_str, _) in grid:
        if d == 0:  # Sunday = first day of column
            m = int(date_str[5:7])
            if m not in month_positions:
                month_positions[m] = w
    for m, w in month_positions.items():
        x = left_margin + w * (BOX_SIZE + BOX_GAP)
        parts.append(f'<text x="{x}" y="{top_margin - 8}" font-size="9">{MONTH_LABELS[m-1]}</text>')
    
    # Grid cells
    cell_idx = 0
    for (w, d, date_str, level) in grid:
        x = left_margin + w * (BOX_SIZE + BOX_GAP)
        y = top_margin + d * (BOX_SIZE + BOX_GAP)
        color = LEVELS.get(level, LEVELS[0])
        delay = cell_idx * CELL_DELAY
        parts.append(f'<rect class="cell" x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="2" fill="{color}" style="animation-delay: {delay:.3f}s"><title>{date_str}</title></rect>')
        cell_idx += 1
    
    # Stats below grid
    stat_items = [
        ("Total", str(stats.get("total", 0))),
        ("Current Streak", f"{stats.get('current_streak', 0)}d"),
        ("Longest Streak", f"{stats.get('longest_streak', 0)}d"),
        ("Active Days", str(stats.get("active_days", 0))),
    ]
    sx = left_margin
    for label, val in stat_items:
        parts.append(f'<text class="stat-label" x="{sx}" y="{stats_y}">{label}</text>')
        parts.append(f'<text class="stat-value" x="{sx}" y="{stats_y + 16}">{val}</text>')
        sx += 140
    
    # Legend: Less □□□□□ More
    lx = svg_w - 180
    parts.append(f'<text x="{lx}" y="{legend_y}" font-size="9">Less</text>')
    lx += 28
    for lvl in range(5):
        parts.append(f'<rect x="{lx}" y="{legend_y - 9}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="2" fill="{LEVELS[lvl]}"/>')
        lx += BOX_SIZE + 3
    parts.append(f'<text x="{lx + 2}" y="{legend_y}" font-size="9">More</text>')
    
    parts.append('</svg>')
    return '\n'.join(parts)

def main():
    data = load_data()
    print(f"[heatmap] Loaded {len(data['days'])} days for {data['user']}")
    svg = render_svg(data)
    with open(OUT, 'w') as f:
        f.write(svg)
    print(f"[heatmap] Wrote {OUT}")

if __name__ == '__main__':
    main()
