import requests

TOKEN = "23350~P3WWL4ZhazN3LGnueK2WnRWcnvLzT8wFv6fXw6uGQEtBUAtZ77uBWfLrEXBxWWZt"
BASE = "https://harveymuddcollege.instructure.com/api/v1"

headers = {"Authorization": f"Bearer {TOKEN}"}

response = requests.get(f"{BASE}/courses", headers=headers,
                        params={"enrollment_state": "active", "per_page": 50})

courses = response.json()
for course in courses:
    print(course.get("name"), course.get("id"))