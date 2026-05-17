import os
import httpx
import subprocess
import signal
import logging
import sys
from celery_app import celery_app
import state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
PID_FILE = os.path.join(os.path.dirname(__file__), "pipeline.pid")


@celery_app.task(name="tasks.post_attention_batch")
def post_attention_batch():
    if not state.is_active():
        print("No active session — skipping attention post")
        return

    session_id = state.get_session_id()
    snapshot   = state.get_and_clear()

    if not snapshot:
        print("No attention data to post")
        return

    payload = {"logs": snapshot}

    try:
        response = httpx.post(
            f"{BACKEND_URL}/sessions/{session_id}/attention",
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
        print(f"Posted {len(snapshot)} logs → {response.json()}")

    except httpx.HTTPError as e:
        logger.error(f"Failed to post attention batch: {e}")


@celery_app.task(name="tasks.start_cv_pipeline")
def start_cv_pipeline():
    """Starts the CV pipeline (main.py) as a subprocess."""
    if os.path.exists(PID_FILE):
        # Check if process is actually running
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0) # Signals 0 does nothing but checks if PID exists
            logger.info(f"Pipeline already running with PID: {pid}")
            return
        except (ProcessLookupError, ValueError, OSError):
            logger.info("Stale PID file found. Cleaning up.")
            os.remove(PID_FILE)

    try:
        # Run main.py from the cv_worker directory
        worker_dir = os.path.dirname(__file__)
        # Ensure we use the same python interpreter
        process = subprocess.Popen(
            [sys.executable, "-u", "main.py"],
            cwd=worker_dir,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            env=os.environ.copy()
        )
        pid = process.pid
        logger.info(f"Started CV pipeline with PID: {pid}")

        with open(PID_FILE, "w") as f:
            f.write(str(pid))

    except Exception as e:
        logger.error(f"Failed to start CV pipeline: {e}")


@celery_app.task(name="tasks.stop_cv_pipeline")
def stop_cv_pipeline():
    """Stops the CV pipeline by killing the process stored in the PID file."""
    if not os.path.exists(PID_FILE):
        logger.info("No PID file found. Pipeline might not be running.")
        return

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        logger.info(f"Stopping CV pipeline with PID: {pid}")
        os.kill(pid, signal.SIGTERM)
        
        # Cleanup
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            
        logger.info("CV pipeline stopped and PID file removed.")

    except ProcessLookupError:
        logger.warning(f"Process with PID {pid} not found. Cleaning up PID file.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        logger.error(f"Failed to stop CV pipeline: {e}")