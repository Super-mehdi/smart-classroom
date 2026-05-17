import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_sessions():
    # 1. Login as teacher1
    print("Logging in as teacher1...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "teacher1@smartclass.com",
        "password": "teacher123"
    })
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get my info to confirm ID
    me = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()
    print(f"Logged in as: {me['full_name']} (ID: {me['id']})")

    # 3. Start a session for class 1
    print("Starting session for class 1...")
    res = requests.post(f"{BASE_URL}/sessions/start", headers=headers, json={"class_id": 1})
    if res.status_code != 200:
        print(f"Start session failed: {res.text}")
        return
    session_id = res.json()["session_id"]
    print(f"Session started with ID: {session_id}")

    # 4. List sessions
    print("Listing sessions...")
    res = requests.get(f"{BASE_URL}/sessions", headers=headers)
    print(f"Sessions: {res.json()}")

    # 5. Stop session
    print(f"Stopping session {session_id}...")
    res = requests.post(f"{BASE_URL}/sessions/{session_id}/stop", headers=headers)
    if res.status_code != 200:
        print(f"Stop session failed: {res.text}")
        return
    print(f"Session stopped at: {res.json()['ended_at']}")

    # 6. Try to start session for someone else's class (class 3 belongs to teacher 2)
    print("Trying to start session for teacher 2's class (should fail)...")
    res = requests.post(f"{BASE_URL}/sessions/start", headers=headers, json={"class_id": 3})
    print(f"Result (expected 403): {res.status_code}")

if __name__ == "__main__":
    test_sessions()
