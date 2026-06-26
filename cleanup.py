import requests

BASE_URL = "http://localhost:8889"
MY_KEY = "***"

HEADERS = {
    "Authorization": f"Bearer {MY_KEY}",
    "Content-Type": "application/json"
}

# Find the test item
res = requests.get(f"{BASE_URL}/api/v1/boards", headers=HEADERS)
data = res.json()

test_items = [i for i in data['items'] if i['text'] == 'New test item']

if test_items:
    print(f"Found {len(test_items)} test item(s)")
    for item in test_items:
        print(f"  Deleting item id={item['id']}...")
        requests.delete(f"{BASE_URL}/api/v1/items/{item['id']}", headers=HEADERS)
    print("✓ Cleanup complete")
else:
    print("No test items found")
