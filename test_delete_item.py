import requests

BASE_URL = "http://localhost:8889"
MY_KEY = "***"

HEADERS = {
    "Authorization": f"Bearer {MY_KEY}",
    "Content-Type": "application/json"
}

# Get board state
res = requests.get(f"{BASE_URL}/api/v1/boards", headers=HEADERS)
data = res.json()

# Find a bucket with items
bucket = [b for b in data['buckets'] if b['column_id'] == 1][0]
bucket_items = [i for i in data['items'] if i['bucket_id'] == bucket['id']]

if not bucket_items:
    print(f"No items in bucket '{bucket['name']}'")
    exit(1)

print(f"Bucket: {bucket['name']} ({len(bucket_items)} items)")

# Get the first item
item_to_delete = bucket_items[0]
print(f"\nDeleting item: '{item_to_delete['text']}' (id={item_to_delete['id']})")

# Delete the item
delete_res = requests.delete(
    f"{BASE_URL}/api/v1/items/{item_to_delete['id']}",
    headers=HEADERS
)

print(f"Delete response: {delete_res.json()}")

# Verify deletion
verify_res = requests.get(f"{BASE_URL}/api/v1/boards")
verify_data = verify_res.json()

remaining_items = [i for i in verify_data['items'] if i['bucket_id'] == bucket['id']]
print(f"\n✓ Item deleted. Remaining items in '{bucket['name']}': {len(remaining_items)}")

# Create a new item to test adding
print("\nCreating a new item to test...")
new_item_res = requests.post(
    f"{BASE_URL}/api/v1/items",
    headers=HEADERS,
    json={
        "bucket_id": bucket['id'],
        "text": "New test item",
        "done": False
    }
)
print(f"Create response: {new_item_res.json()}")

# Verify
final_res = requests.get(f"{BASE_URL}/api/v1/boards")
final_data = final_res.json()
final_items = [i for i in final_data['items'] if i['bucket_id'] == bucket['id']]
print(f"✓ Total items now: {len(final_items)}")
