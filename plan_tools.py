import json
from datetime import date, datetime, timedelta

PLAN_PATH = "plan_reference.json"

def load_plan():
    with open(PLAN_PATH, "r") as f:
        return json.load(f)

def get_week(plan, week_label: str):
    for w in plan["weeks"]:
        if w["week_label"].lower() == week_label.lower():
            return w
    return None

def pretty_week(week):
    lines = []
    lines.append(f"{week['week_label']} ({week['date_range']}) — {week.get('goal','')}".strip())
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        if day in week["sessions"]:
            lines.append(f"  {day}: {week['sessions'][day]}")
    return "\n".join(lines)

def get_date_range(week):
    # expects "YYYY-MM-DD to YYYY-MM-DD"
    start_s, end_s = [s.strip() for s in week["date_range"].split("to")]
    start = datetime.strptime(start_s, "%Y-%m-%d").date()
    end = datetime.strptime(end_s, "%Y-%m-%d").date()
    return start, end

def workout_on(plan, d: date):
    # find week containing date; then map day name to session
    dow = d.strftime("%A")
    for w in plan["weeks"]:
        start, end = get_date_range(w)
        if start <= d <= end:
            return w["week_label"], dow, w["sessions"].get(dow)
    return None, dow, None

def week_for_date(plan, d: date):
    for w in plan["weeks"]:
        start, end = get_date_range(w)
        if start <= d <= end:
            return w
    return None

def next_week(plan, d: date):
    # find the next week starting after d
    candidates = []
    for w in plan["weeks"]:
        start, end = get_date_range(w)
        if start > d:
            candidates.append((start, w))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1] if candidates else None
