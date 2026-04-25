from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timezone
from gradescope_data import GRADESCOPE_ASSIGNMENTS

app = Flask(__name__)
CORS(app)

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

def get_canvas_assignments():
    now = datetime.now(timezone.utc)
    upcoming = []
    for course_name, course_id in COURSES.items():
        r = requests.get(f"{BASE}/courses/{course_id}/assignments",
                         headers=headers,
                         params={"per_page": 50, "order_by": "due_at"})
        for a in r.json():
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
                "due": due_dt.isoformat(),
                "hours_left": round(hours_left, 1),
                "url": a.get("html_url"),
                "source": "canvas"
            })
    return upcoming

def get_gradescope():
    now = datetime.now(timezone.utc)
    result = []
    for a in GRADESCOPE_ASSIGNMENTS:
        due_dt = datetime.fromisoformat(a["due"])
        if due_dt.tzinfo is None:
            due_dt = due_dt.replace(tzinfo=timezone.utc)
        hours_left = (due_dt - now).total_seconds() / 3600
        if hours_left > 0:
            result.append({**a, "due": due_dt.isoformat(), "hours_left": round(hours_left, 1)})
    return result

@app.route("/api/assignments")
def assignments():
    canvas = get_canvas_assignments()
    gradescope = get_gradescope()
    all_assignments = canvas + gradescope
    seen = set()
    merged = []
    for a in all_assignments:
        if a["name"] not in seen:
            seen.add(a["name"])
            merged.append(a)
    merged.sort(key=lambda x: x["due"])
    return jsonify(merged)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    