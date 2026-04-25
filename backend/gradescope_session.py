import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json

class GradescopeSession:
    BASE = "https://www.gradescope.com"

    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.cookies.set(
            "_gradescope_session", session_cookie, domain="www.gradescope.com"
        )
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.gradescope.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def get_courses(self):
        r = self.session.get(f"{self.BASE}/")
        soup = BeautifulSoup(r.text, "html.parser")
        courses = []
        seen = set()

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if "/courses/" not in href:
                continue
            parts = href.split("/courses/")
            if len(parts) < 2:
                continue
            course_id = parts[1].split("/")[0]
            if not course_id.isdigit() or course_id in seen:
                continue
            seen.add(course_id)

            name = ""
            h3 = a.find("h3")
            if h3:
                name = h3.text.strip()
            if not name:
                strong = a.find("strong")
                name = strong.text.strip() if strong else a.text.strip()
            name = " ".join(name.split())
            if not name:
                name = f"Course {course_id}"

            courses.append({
                "id": course_id,
                "name": name,
                "url": f"{self.BASE}/courses/{course_id}"
            })

        return courses

    def get_assignments(self, course_id, course_name=""):
        url = f"{self.BASE}/courses/{course_id}/assignments"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        now = datetime.now(timezone.utc)
        assignments = []

        rows = soup.select("tr.js-assignmentTableRow")
        if not rows:
            rows = soup.select("tr")

        for row in rows:
            name_el = (
                row.select_one("a.assignment-name") or
                row.select_one(".table--primaryLink") or
                row.select_one("td a") or
                row.select_one(".js-assignmentTitle")
            )
            if not name_el:
                continue
            name = name_el.text.strip()
            if not name or name.lower() in ["name", "assignment"]:
                continue

            due_el = (
                row.select_one("time[datetime]") or
                row.select_one(".submissionTimeChart--dueDate time") or
                row.select_one("[data-due-date]")
            )

            due_dt = None
            hours_left = None

            if due_el:
                due_str = due_el.get("datetime") or due_el.get("data-due-date", "")
                if due_str:
                    try:
                        due_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                        hours_left = (due_dt - now).total_seconds() / 3600
                    except:
                        pass

            if hours_left is not None and hours_left < 0:
                continue

            status_el = row.select_one(".submissionStatus, .submissionStatus--text")
            status = status_el.text.strip() if status_el else "No Submission"

            link = f"{self.BASE}/courses/{course_id}/assignments"
            if name_el and name_el.get("href"):
                link = self.BASE + name_el["href"]

            assignments.append({
                "name": name,
                "course": course_name,
                "due": due_dt.isoformat() if due_dt else None,
                "hours_left": round(hours_left, 1) if hours_left else None,
                "url": link,
                "status": status,
                "source": "gradescope"
            })

        return assignments

    def get_all_upcoming(self):
        print("Fetching Gradescope courses...")
        courses = self.get_courses()
        print(f"Found {len(courses)} courses")
        all_assignments = []
        for c in courses:
            print(f"  Checking {c['name']} (ID: {c['id']})...")
            try:
                assignments = self.get_assignments(c["id"], c["name"])
                print(f"    {len(assignments)} upcoming")
                all_assignments.extend(assignments)
            except Exception as e:
                print(f"    Error: {e}")
        return all_assignments
