import requests

BASE_URL = "http://localhost:8889"
MY_KEY = "***"

HEADERS = {
    "Authorization": f"Bearer {MY_KEY}",
    "Content-Type": "application/json"
}

# Get a bucket
res = requests.get(f"{BASE_URL}/api/v1/boards", headers=HEADERS)
data = res.json()

bucket = [b for b in data['buckets'] if b['column_id'] == 1][0]
print(f"Bucket: {bucket['name']}")

# Create an item (should get date_created auto-set)
print("\n1. Creating item...")
r = requests.post(
    f"{BASE_URL}/api/v1/items",
    headers=HEADERS,
    json={"bucket_id": bucket['id'], "text": "Test item with dates", "done": False}
)
item = r.json()
print(f"   Created: {item}")
print(f"   date_created: {item['date_created']}")
print(f"   date_completed: {item.get('date_completed')}")

# Mark it done (should get date_completed auto-set)
print("\n2. Marking item done...")
r = requests.patch(
    f"{BASE_URL}/api/v1/items/{item['id']}",
    headers=HEADERS,
    json={"done": True}
)
item = r.json()
print(f"   date_completed: {item['date_completed']}")

# Verify both dates
print("\n3. Verifying...")
r = requests.get(f"{BASE_URL}/api/v1/items/{item['id']}")
# Actually there's no GET item endpoint, let's just check via the bucket
r = requests.get(f"{BASE_URL}/api/v1/boards", headers=HEADERS)
data = r.json()
item = [i for i in data['items'] if i['text'] == 'Test item with dates'][0]
print(f"   date_created: {item['date_created']}")
print(f"   date_completed: {item['date_completed']}")

# Cleanup
print("\n4. Cleaning up...")
requests.delete(f"{BASE_URL}/api/v1/items/{item['id']}", headers=HEADERS)
print("   Done!")
