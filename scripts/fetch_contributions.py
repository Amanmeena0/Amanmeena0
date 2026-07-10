#!/usr/bin/env python3
"""fetch_contributions.py – scrape GitHub contribution data (no auth)."""
import os
import json
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────
GH_PROFILE_USER = os.environ.get("GH_PROFILE_USER", "Amanmeena0")
OUT_DIR         = "data"
OUT_FILE        = os.path.join(OUT_DIR, "contributions.json")
# ── END CONFIG ────────────────────────────────────────────────────

def fetch_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    print(f"[fetch] Scraping {url}...")
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    days = []
    # GitHub renders contribution cells as <td> with data-date and data-level
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date", "")
        level = int(td.get("data-level", 0))
        # Try to get count from tooltip or aria-label or the tool-tip element
        count = 0
        # Check for tool-tip child element
        tooltip = td.find("tool-tip") or td.find("span", class_="sr-only")
        if tooltip:
            text = tooltip.get_text()
            match = re.search(r"(\d+)\s+contribution", text)
            if match:
                count = int(match.group(1))
        if not date:
            continue
        days.append({"date": date, "count": count, "level": level})
    
    return days

def compute_stats(days):
    # If actual counts weren't available, estimate from levels
    level_estimates = {0: 0, 1: 2, 2: 5, 3: 8, 4: 12}
    for d in days:
        if d["count"] == 0 and d["level"] > 0:
            d["count"] = level_estimates.get(d["level"], 0)
    
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    
    # Current streak
    sorted_days = sorted(days, key=lambda d: d["date"], reverse=True)
    current_streak = 0
    for d in sorted_days:
        if d["count"] > 0:
            current_streak += 1
        else:
            break
    
    # Longest streak
    sorted_asc = sorted(days, key=lambda d: d["date"])
    longest = 0
    current = 0
    for d in sorted_asc:
        if d["count"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    
    # Best day
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    
    return {
        "total": total,
        "active_days": active_days,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best["date"],
        "best_day_count": best["count"],
    }

def main():
    days = fetch_contributions(GH_PROFILE_USER)
    print(f"[fetch] Got {len(days)} days of data")
    
    stats = compute_stats(days)
    print(f"[fetch] Total: {stats['total']} contributions, Current streak: {stats['current_streak']} days")
    
    os.makedirs(OUT_DIR, exist_ok=True)
    data = {"user": GH_PROFILE_USER, "days": days, "stats": stats, "fetched_at": datetime.utcnow().isoformat()}
    with open(OUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[fetch] Saved to {OUT_FILE}")

if __name__ == "__main__":
    main()
