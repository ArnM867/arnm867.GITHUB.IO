import requests
from datetime import datetime, timezone
from gradescope_data import GRADESCOPE_ASSIGNMENTS
from datetime import datetime, timezone
TOKEN = "23350~P3WWL4ZhazN3LGnueK2WnRWcnvLzT8wFv6fXw6uGQEtBUAtZ77uBWfLrEXBxWWZt"
BASE = "https://harveymuddcollege.instructure.com/api/v1"
headers = {"Authorization": f"Bearer {TOKEN}"}

COURSES = {
    "Critical Inquiry": "3201",
    "Chemistry 042": "3134",
    "Chem Lab 024": "3342",
    "Math 73": "3340",
    "Physics 024": "3338",
}

def get_gradescope_assignments():
    now = datetime.now(timezone.utc)
    result = []
    for a in GRADESCOPE_ASSIGNMENTS:
        due_dt = datetime.fromisoformat(a["due"])
        if due_dt.tzinfo is None:
            due_dt = due_dt.replace(tzinfo=timezone.utc)
        hours_left = (due_dt - now).total_seconds() / 3600
        if hours_left > 0:
            result.append({**a, "due": due_dt, "hours_left": round(hours_left, 1)})
    return result

def get_upcoming_assignments():
    now = datetime.now(timezone.utc)
    upcoming = []

    for course_name, course_id in COURSES.items():
        r = requests.get(f"{BASE}/courses/{course_id}/assignments",
                         headers=headers,
                         params={"per_page": 50, "order_by": "due_at"})
        assignments = r.json()

        for a in assignments:
            due = a.get("due_at")
            if not due:
                continue
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            if due_dt < now:
                continue

            hours_left = (due_dt - now).total_seconds() / 3600

            upcoming.append({
                "course": course_name,
                "name": a.get("name"),
                "due": due_dt,
                "hours_left": round(hours_left, 1),
                "url": a.get("html_url"),
            })

    upcoming.sort(key=lambda x: x["due"])
    return upcoming

def generate_daily_plan(assignments):
    print("\n MUDDMATE — YOUR PLAN FOR TODAY")
    print("=" * 45)

    if not assignments:
        print("Nothing due soon. Great job staying ahead!")
        return

    print(f"\nYou have {len(assignments)} upcoming assignments:\n")

    for i, a in enumerate(assignments, 1):
        days = int(a["hours_left"] // 24)
        hours = int(a["hours_left"] % 24)
        time_str = f"{days}d {hours}h" if days > 0 else f"{hours}h"
        urgency = "🔴" if a["hours_left"] < 24 else "🟡" if a["hours_left"] < 72 else "🟢"

        print(f"{urgency} [{a['course']}] {a['name']}")
        print(f"   Due in {time_str}")
        print(f"   → {a['url']}")
        print()

canvas_assignments = get_upcoming_assignments()
gradescope_assignments = get_gradescope_assignments()

# Merge and deduplicate by name
all_assignments = canvas_assignments + gradescope_assignments
seen = set()
merged = []
for a in all_assignments:
    if a["name"] not in seen:
        seen.add(a["name"])
        merged.append(a)

merged.sort(key=lambda x: x["due"])
generate_daily_plan(merged)