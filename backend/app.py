from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

CANVAS_BASE = "https://harveymuddcollege.instructure.com/api/v1"
SKIP_NAMES = {"Title IX", "Orientation", "Core Skills", "Resources", "Preview"}


def _canvas_token():
    return request.headers.get("X-Canvas-Token") or request.args.get("token", "")


def _canvas_get(path, token, **params):
    return requests.get(
        f"{CANVAS_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=10,
    )


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/courses")
def get_courses():
    token = _canvas_token()
    if not token:
        return jsonify({"error": "Missing X-Canvas-Token header"}), 401

    r = _canvas_get("/courses", token, enrollment_state="active", per_page=50)
    if not r.ok:
        return jsonify({"error": "Canvas auth failed"}), 401

    courses = [
        {"id": str(c["id"]), "name": c["name"]}
        for c in r.json()
        if c.get("name") and not any(s in c["name"] for s in SKIP_NAMES)
    ]
    return jsonify(courses)


@app.route("/api/assignments")
def get_assignments():
    token = _canvas_token()
    if not token:
        return jsonify({"error": "Missing X-Canvas-Token header"}), 401

    course_ids = request.args.getlist("course_id")
    course_name_map = {}

    if not course_ids:
        r = _canvas_get("/courses", token, enrollment_state="active", per_page=50)
        if not r.ok:
            return jsonify({"error": "Canvas auth failed"}), 401
        for c in r.json():
            if c.get("name") and not any(s in c["name"] for s in SKIP_NAMES):
                cid = str(c["id"])
                course_ids.append(cid)
                course_name_map[cid] = c["name"]
    else:
        for cid in course_ids:
            course_name_map[cid] = request.args.get(f"name_{cid}", f"Course {cid}")

    now = datetime.now(timezone.utc)
    all_assignments = []

    for cid in course_ids:
        r = _canvas_get(f"/courses/{cid}/assignments", token, per_page=50, order_by="due_at")
        if not r.ok:
            continue
        for a in r.json():
            due = a.get("due_at")
            if not due:
                continue
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            if due_dt < now:
                continue
            hours_left = (due_dt - now).total_seconds() / 3600
            all_assignments.append({
                "course": course_name_map.get(cid, f"Course {cid}"),
                "name": a.get("name"),
                "due": due_dt.isoformat(),
                "hours_left": round(hours_left, 1),
                "url": a.get("html_url"),
                "source": "canvas",
            })

    all_assignments.sort(key=lambda x: x["due"])
    return jsonify(all_assignments)


@app.route("/api/gradescope")
def get_gradescope():
    from gradescope_session import GradescopeSession
    cookie = request.headers.get("X-Gradescope-Cookie") or request.args.get("cookie", "")
    if not cookie:
        return jsonify({"error": "Missing X-Gradescope-Cookie header"}), 401

    course_id = request.args.get("course_id")
    course_name = request.args.get("course_name", "")

    try:
        gs = GradescopeSession(cookie)
        data = gs.get_assignments(course_id, course_name) if course_id else gs.get_all_upcoming()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
