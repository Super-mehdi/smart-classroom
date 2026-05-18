import os
import time
import requests
import logging
import threading
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("SessionManager")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WORKER_EMAIL = os.getenv("WORKER_EMAIL", "")
WORKER_PASSWORD = os.getenv("WORKER_PASSWORD", "")

def login():
    url = f"{BACKEND_URL}/api/auth/login"
    if not WORKER_EMAIL or not WORKER_PASSWORD:
        logger.error("WORKER_EMAIL or WORKER_PASSWORD not set in environment.")
        return None
    
    payload = {
        "email": WORKER_EMAIL,
        "password": WORKER_PASSWORD
    }
    try:
        logger.info(f"Attempting login for {WORKER_EMAIL} at {url}")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if token:
            logger.info("Login successful, token obtained.")
            return token
        else:
            logger.error(f"Login response missing access_token. Response: {data}")
            return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Login HTTP error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return None

def get_active_session(token):
    url = f"{BACKEND_URL}/api/sessions"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        sessions = response.json()
        
        # sessions shape: [{ session_id, class_id, started_at, ended_at }]
        active_sessions = [s for s in sessions if s.get("ended_at") is None]
        
        if active_sessions:
            # Return the id of the first session where ended_at is null
            session_id = active_sessions[0].get("session_id")
            logger.info(f"Found active session: {session_id}")
            return session_id
        
        logger.info("No active sessions found.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to fetch sessions (HTTP {e.response.status_code}): {e.response.text}")
        if e.response.status_code == 401:
            return "EXPIRED"
        return None
    except Exception as e:
        logger.error(f"Failed to fetch active session: {e}")
        return None

class SessionManager:
    def __init__(self):
        self.session_id = None
        self._stop_event = threading.Event()
        self._thread = None

    def _loop(self):
        token = None
        while not self._stop_event.is_set():
            if not token:
                token = login()
            
            if token:
                res = get_active_session(token)
                if res == "EXPIRED":
                    token = None
                    continue
                
                new_session_id = res
                if new_session_id != self.session_id:
                    logger.info(f"Session ID changed: {self.session_id} -> {new_session_id}")
                    self.session_id = new_session_id
            else:
                logger.warning("No token available, retrying login in 30s.")

            # Wait for 30 seconds or until stopped
            self._stop_event.wait(30)

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("SessionManager already started.")
            return
        
        logger.info("Starting SessionManager...")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        logger.info("Stopping SessionManager...")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            logger.info("SessionManager stopped.")

session_manager = SessionManager()
