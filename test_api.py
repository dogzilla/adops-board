import requests
import json

BASE_URL = "http://localhost:8889"
API_KEY = "***"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test creating a bucket
print("Creating bucket...")
r = requests.post(f"{BASE_URL}/api/v1/buckets", headers=headers, json={"column_id": 2, "name": "Test Card", "description": "A test card"})
print("Create:", r.json())

bucket_id = r.json()["id"]

# Test moving the bucket
print("\nMoving bucket...")
r = requests.post(f"{BASE_URL}/api/v1/buckets/{bucket_id}/move", headers=headers, json={"column_id": 3})
print("Move:", r.json())

# Test updating the bucket
print("\nUpdating bucket...")
r = requests.patch(f"{BASE_URL}/api/v1/buckets/{bucket_id}", headers=headers, json={"name": "Updated Card", "description": "Updated test card"})
print("Update:", r.json())

# Test deleting the bucket
print("\nDeleting bucket...")
r = requests.delete(f"{BASE_URL}/api/v1/buckets/{bucket_id}", headers=headers)
print("Delete:", r.json())

# Verify deletion
print("\nVerifying deletion...")
r = requests.get(f"{BASE_URL}/api/v1/boards")
data = r.json()
buckets = [b for b in data["buckets"] if b["name"] == "Updated Card"]
print(f"  Updated Card exists: {len(buckets) > 0}")

# Show final state
print(f"\nFinal state: {len(data['columns'])} columns, {len(data['buckets'])} buckets, {len(data['items'])} items")
