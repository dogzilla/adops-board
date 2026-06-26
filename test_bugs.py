#!/usr/bin/env python3
"""Test Bug #1 and Bug #2 from Bob's report."""
import requests

BASE = "http://localhost:8889"
KEY = "kanban-secret-key"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def test():
    # Setup defaults
    r = requests.get(f"{BASE}/api/v1/setup", headers=HEADERS)
    print(f"Setup: {r.status_code}")
    
    # Create a bucket
    r = requests.post(f"{BASE}/api/v1/buckets", headers=HEADERS, json={"column_id": 1, "name": "Test Card"})
    print(f"Create bucket: {r.status_code} → {r.json()}")
    bucket_id = r.json()["id"]
    
    # Bug #1: PATCH with assigned_to
    print(f"\n=== Bug #1: PATCH /buckets/{bucket_id} with assigned_to ===")
    r = requests.patch(f"{BASE}/api/v1/buckets/{bucket_id}", headers=HEADERS, json={"assigned_to": "Carson Harris"})
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    
    # Verify it stuck
    r = requests.get(f"{BASE}/api/v1/boards")
    buckets = r.json()["buckets"]
    b = next((b for b in buckets if b["id"] == bucket_id), None)
    print(f"Verify assigned_to: {b.get('assigned_to')}")
    
    # Bug #2: POST with id field
    print(f"\n=== Bug #2: POST /buckets with id field ===")
    r = requests.post(f"{BASE}/api/v1/buckets", headers=HEADERS, json={"id": 99, "column_id": 1, "name": "ID Test"})
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

if __name__ == "__main__":
    test()
