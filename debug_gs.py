import requests
from bs4 import BeautifulSoup

COOKIE = "RmdnYU5qbnVmRnNMQ1JTNGJiajlGMXQvZXAvaWtybHlkMzRmRTU5UCtNSlAxMmpDaHRwenlMaldnclEvL2NjSFd2UDZNVm0zNGh4VWxEVXFWUGMwdU8yeWRhbXVRNzBsWjd0UUVTdko1SlZhZUtHTlFRUkxjSVNhdFBCTkVES3pQOWMrYXBNRS9iVHF0TG9qR0dKeis2NTJMN0V6L0hSR0FIdEdvTGdEaE5tM3c2cnNLREt4eXl2NlRJcWE0KzZsZ1I4UzIzbEJZQldldnZVRkNjTUNNbFkwM2RhNGZMSS9DUjF6SFNpSEpPNXBxaXJDeE5VMzF0Q3dhQndmczJrZ2VXd3YvUTk5Smp6T1M0UThIUjY5ZSt1ZUtkZ1MrQUtmNU9iWEZLcnFqcjMyV0NRd1h4bjZWT0xyY0MyWkFiSGZJTFY0WnJ5NEtFa0ZoVmovWHV6bWpQMDlIZllVZXpkSHhaVDY4c3ZlWHhrPS0tZDhUNFpKaFRveUpyRFNZai83MWFsZz09--b0879dff6fa444cbdc658aa7795719ffd0cc2d46"

s = requests.Session()
s.cookies.set("_gradescope_session", COOKIE, domain="www.gradescope.com")
s.headers.update({"User-Agent": "Mozilla/5.0"})

r = s.get("https://www.gradescope.com/courses/1217636/assignments")
print("Status:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.text if soup.title else "none")
print("First 1000 chars:")
print(r.text[:1000])