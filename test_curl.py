import requests
import json

url = "http://localhost:8889/api/v1/items/117"
headers = {
    "Authorization": "Bearer ***",
    "Content-Type": "application/json"
}

# First, let's see what the current item looks like
r = requests.get("http://localhost:8889/api/v1/boards", headers={"Authorization": "Bearer ***"})
data = r.json()
item = [i for i in data['items'] if i['id'] == 117][0]
print(f"Current item: {json.dumps(item, indent=2)}")

# Now PATCH it
print("\nPATCHing...")
r = requests.patch(url, headers=headers, json={"done": True})
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Content: {repr(r.content)}")
print(f"Text: {r.text}")
