import sys
import os
import json
import re
import datetime
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username="manyakalia1", output_path="data/contributions.json"):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"[+] Fetching GitHub contributions for '{username}'...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[!] Error fetching contributions HTML (status {response.status_code})")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Parse day cells
    cells = soup.find_all(["td", "rect"], class_=lambda c: c and "ContributionCalendar-day" in c)
    if not cells:
        print("[!] Warning: No contribution cells found in HTML.")

    days_data = []
    total_contributions = 0

    for cell in cells:
        cid = cell.get("id")
        date_str = cell.get("data-date")
        level_str = cell.get("data-level", "0")
        try:
            level = int(level_str)
        except ValueError:
            level = 0

        # Find tooltip associated with this day cell
        tt = soup.find("tool-tip", attrs={"for": cid}) if cid else None
        tt_text = tt.text.strip() if tt else ""

        # Extract contribution count from tooltip text
        match = re.search(r'(\d+)\s+contribution', tt_text)
        count = int(match.group(1)) if match else 0

        if date_str:
            days_data.append({
                "date": date_str,
                "count": count,
                "level": level
            })
            total_contributions += count

    # Sort days chronologically
    days_data.sort(key=lambda x: x["date"])

    # Calculate Derived Stats
    # 1. Best Day
    best_day = {"date": None, "count": 0}
    for day in days_data:
        if day["count"] > best_day["count"]:
            best_day = {"date": day["date"], "count": day["count"]}

    # 2. Monthly Totals
    monthly_totals = {}
    for day in days_data:
        month_key = day["date"][:7]  # "YYYY-MM"
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + day["count"]

    # 3. Streaks (Current Streak & Longest Streak)
    longest_streak = 0
    temp_streak = 0

    for day in days_data:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate Current Streak starting from the most recent day backwards
    current_streak = 0
    if days_data:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        # Check from last day backwards
        idx = len(days_data) - 1
        # If today has 0, check if yesterday was part of active streak
        if days_data[idx]["count"] == 0 and idx > 0:
            idx -= 1
        
        while idx >= 0 and days_data[idx]["count"] > 0:
            current_streak += 1
            idx -= 1

    payload = {
        "username": username,
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": days_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[+] Saved contributions data to '{output_path}' ({len(days_data)} days, {total_contributions} total contributions)")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "manyakalia1"
    fetch_contributions(user)
