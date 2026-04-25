from gradescopeapi.classes.connection import GSConnection

conn = GSConnection()
conn.login("armalik@hmc.edu", "yourpassword")

courses = conn.account.courses
for course_id, course in courses.items():
    print(f"\n--- {course.name} (ID: {course_id}) ---")
    assignments = conn.get_assignments(course_id)
    for a in assignments:
        print(f"  {a.name} | due: {a.due_date}")
