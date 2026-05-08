import os
import requests
from datetime import datetime, timezone

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def post_attendance(session_id: int, face_count: int, enrolled_count: int):
    """
    POST face count to the backend attendance endpoint.
    """
    url = f"{BACKEND_URL}/api/sessions/{session_id}/attendance"
    payload = {
        "face_count":     face_count,
        "enrolled_count": enrolled_count,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Attendance posted: {face_count}/{enrolled_count} present")
    except requests.exceptions.ConnectionError:
        print("WARNING: Could not reach backend. Is it running?")
    except requests.exceptions.HTTPError as e:
        print(f"WARNING: Backend returned error: {e.response.status_code} {e.response.text}")
    except Exception as e:
        print(f"WARNING: Failed to post attendance: {e}")