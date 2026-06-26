import requests
import json

BASE_URL = "http://localhost:8889"

# Test export endpoint
print("Testing export endpoint...")

# Get all data
res = requests.get(f"{BASE_URL}/api/v1/export?completed=true")
all_data = res.json()
print(f"All: {len(all_data['buckets'])} buckets, {len(all_data['items'])} items")

# Get excluding completed
res = requests.get(f"{BASE_URL}/api/v1/export?completed=false")
filtered_data = res.json()
print(f"Filtered: {len(filtered_data['buckets'])} buckets, {len(filtered_data['items'])} items")

# Check the difference
all_bucket_ids = {b['id'] for b in all_data['buckets']}
filtered_bucket_ids = {b['id'] for b in filtered_data['buckets']}
excluded = all_bucket_ids - filtered_bucket_ids
print(f"Excluded buckets: {len(excluded)}")

# Verify excluded cards are actually completed
if excluded:
    for bucket_id in excluded:
        bucket = next(b for b in all_data['buckets'] if b['id'] == bucket_id)
        items = [i for i in all_data['items'] if i['bucket_id'] == bucket_id]
        all_done = all(i['done'] for i in items) if items else False
        print(f"  Bucket {bucket_id}: {bucket['name']}, items: {len(items)}, all_done: {all_done}")

print("\nExport test complete!")
