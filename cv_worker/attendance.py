import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def post_attendance(session_id: int, present: list, absent: list):
    """
    POST recognized students to the backend attendance endpoint.
    present/absent: [{"student_id": "S001", "name": "Mehdi"}, ...]
    """
    url = f"{BACKEND_URL}/api/sessions/{session_id}/attendance"
    payload = {
        "present":   [s["student_id"] for s in present],
        "absent":    [s["student_id"] for s in absent],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Attendance posted: {[s['name'] for s in present]} present")
    except requests.exceptions.ConnectionError:
        print("WARNING: Could not reach backend. Is it running?")
    except requests.exceptions.HTTPError as e:
        print(f"WARNING: Backend returned error: {e.response.status_code} {e.response.text}")
    except Exception as e:
        print(f"WARNING: Failed to post attendance: {e}")