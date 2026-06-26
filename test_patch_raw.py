import requests

BASE_URL = "http://localhost:8889"
MY_KEY = "***"

HEADERS = {
    "Authorization": f"Bearer {MY_KEY}",
    "Content-Type": "application/json"
}

# Mark item 117 as done
r = requests.patch(
    f"{BASE_URL}/api/v1/items/117",
    headers=HEADERS,
    json={"done": True}
)

print("Status:", r.status_code)
print("Raw response:", r.text)
print("JSON:", r.json())
