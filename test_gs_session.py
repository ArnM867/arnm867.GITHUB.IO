from gradescope_session import GradescopeSession

# Paste your FRESH cookie here
COOKIE = "QUIxZlJWeDBMdTJmY0FYSlFPRzhnY0xXWnlxL0dzeDFweGZiMHhVZndKVzBMa2RkbUxiZFFPTC9RNDdrZFhqVHhFd3ZuMnRuQ25nbWg1RGpjSC9WaTZsamJQT25rT3E3RW1JSGt1UjRhQjVJelVUeDlwR0k5ZW44cVB1WVJWTzgzd2hESXZYVElaUDhkVWpabDJBZVJNMG1IVXplS0JMelZqdjBGTVhmZDZKQ0xCa2laYURZUUZqWHJxempoeXd3bEFhUDRWcm1jTk9WdmdSQTljQmtqZG9WT1lTOVFXUHFaUU5sLzRLRWhieWp2T3YvRDhVWmppZUZoMHRzNzZNWHhTaUFLOGZQYnlEdytyY0tDVHU3VVpHUUZodGNpMUVXOTdXY0ptbU4zbnJoTk1qZndYRWtvVkU4M09GTEwzRGVBRUw5bGl0cFBzWHozaDBldlJnY3hRVWpXcGVkQTcxaG1nalQ5SXdJRnhnPS0teitkdHgzaUErRHdPN3IxdEpwZlVkUT09--15ff9a8dd794546c800d40724b5bb08e247b8979"

gs = GradescopeSession(COOKIE)

# First test: known course IDs from screenshot
KNOWN_COURSES = [
    ("1219840", "HMC CHEM 042 SP26"),
    ("1195065", "HMC CHEMISTRY 024 SP26"),
    ("1217636", "HMC PHYSICS 024 SP26"),
    ("1214500", "HMC MATH 073 SP26"),  # guessed ID, may need updating
]

print("=== Testing known course IDs directly ===\n")
from datetime import datetime, timezone
now = datetime.now(timezone.utc)

for course_id, course_name in KNOWN_COURSES:
    print(f"--- {course_name} ---")
    assignments = gs.get_assignments(course_id, course_name)
    if assignments:
        for a in assignments:
            print(f"  {a['name']} | due: {a['due']} | {a['hours_left']}h | {a['status']}")
    else:
        print("  (no upcoming assignments found)")
    print()

print("\n=== Auto-discovering courses ===\n")
courses = gs.get_courses()
for c in courses:
    print(f"  {c['name']} — ID: {c['id']}")
