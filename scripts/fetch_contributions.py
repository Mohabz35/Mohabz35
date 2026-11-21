#!/usr/bin/env python3
"""
Scrapes daily contribution counts directly from GitHub's public contribution calendar fragment.
Requires no personal access tokens, no OAuth, and no GraphQL auth.
Outputs data/contributions.json with raw days and calculated streaks.
"""
import datetime
import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CONFIG_PATH = os.path.join(ROOT, "profile_config.json")
OUT_PATH = os.path.join(ROOT, "data", "contributions.json")


def get_username():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        return sys.argv[1]
    if os.environ.get("GH_USERNAME"):
        return os.environ["GH_USERNAME"]
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if cfg.get("username"):
                    return cfg["username"]
        except Exception:
            pass
    return "octocat"


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://github.com/{username}",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print(f"Warning: No calendar cells found for user '{username}'. Profile might be private or username invalid.", file=sys.stderr)
        # Fallback dummy data for preview
        today = datetime.date.today()
        fallback_days = []
        for i in range(365, -1, -1):
            d = today - datetime.timedelta(days=i)
            fallback_days.append({"date": d.isoformat(), "count": (i % 5 if i % 3 == 0 else 0), "level": (1 if i % 3 == 0 else 0)})
        return fallback_days

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days.append({
            "date": date,
            "count": count,
            "level": int(td.get("data-level") or 0)
        })

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days):
    if not days:
        return 0, None, None
    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(username, days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": datetime.date.today().isoformat(), "count": 0}
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": username,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"] if days else "", "end": days[-1]["date"] if days else ""},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


if __name__ == "__main__":
    user = get_username()
    print(f"Fetching contribution data for '{user}'...")
    try:
        days = fetch_days(user)
        data = build_data(user, days)
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully generated {OUT_PATH}: {data['total_contributions']} total contributions, "
              f"current streak {data['current_streak']['length']} days, longest streak {data['longest_streak']['length']} days.")
    except Exception as e:
        print(f"Error fetching contributions: {e}", file=sys.stderr)
        sys.exit(1)
