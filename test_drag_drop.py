import requests

BASE_URL = "http://localhost:8889"
MY_KEY = "***"

HEADERS = {
    "Authorization": f"Bearer {MY_KEY}",
    "Content-Type": "application/json"
}

# Get current board state
res = requests.get(f"{BASE_URL}/api/v1/boards", headers=HEADERS)
data = res.json()

# Find a bucket in "To Do" column
todo_col = [c for c in data['columns'] if c['name'] == 'To Do'][0]
completed_col = [c for c in data['columns'] if c['name'] == 'Completed'][0]

# Pick a bucket to move
bucket = [b for b in data['buckets'] if b['column_id'] == todo_col['id']][0]
print(f"Moving '{bucket['name']}' from '{todo_col['name']}' to '{completed_col['name']}'...")

# Simulate drag-drop (POST to move endpoint)
move_res = requests.post(
    f"{BASE_URL}/api/v1/buckets/{bucket['id']}/move",
    headers=HEADERS,
    json={"column_id": completed_col['id']}
)

print(f"Move response: {move_res.json()}")

# Verify the move
verify_res = requests.get(f"{BASE_URL}/api/v1/boards")
verify_data = verify_res.json()

moved_bucket = [b for b in verify_data['buckets'] if b['id'] == bucket['id']][0]
new_col_name = [c['name'] for c in verify_data['columns'] if c['id'] == moved_bucket['column_id']][0]

print(f"✓ Bucket '{moved_bucket['name']}' is now in '{new_col_name}'")

# Move it back
print(f"\nMoving it back to '{todo_col['name']}'...")
back_res = requests.post(
    f"{BASE_URL}/api/v1/buckets/{bucket['id']}/move",
    headers=HEADERS,
    json={"column_id": todo_col['id']}
)
print(f"Move back response: {back_res.json()}")

# Final verification
final_res = requests.get(f"{BASE_URL}/api/v1/boards")
final_data = final_res.json()
final_bucket = [b for b in final_data['buckets'] if b['id'] == bucket['id']][0]
final_col_name = [c['name'] for c in final_data['columns'] if c['id'] == final_bucket['column_id']][0]
print(f"✓ Bucket '{final_bucket['name']}' is back in '{final_col_name}'")
print("\n✅ Drag-and-drop API is working correctly!")
