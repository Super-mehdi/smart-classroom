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
    logger.info("Received start_cv_pipeline task")
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            logger.info(f"Pipeline already running with PID: {pid}")
            return
        except (ProcessLookupError, ValueError, OSError):
            logger.info("Stale PID file found. Cleaning up.")
            os.remove(PID_FILE)

    try:
        worker_dir = os.path.dirname(__file__)
        log_path = os.path.join(worker_dir, "pipeline.log")
        logger.info(f"Starting pipeline, logging to {log_path}")

        with open(log_path, "a") as log_file:
            process = subprocess.Popen(
                [sys.executable, "-u", "main.py"],
                cwd=worker_dir,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                env=os.environ.copy(),
                start_new_session=True
            )
            pid = process.pid
            logger.info(f"Successfully started CV pipeline with PID: {pid}")

            with open(PID_FILE, "w") as f:
                f.write(str(pid))

    except Exception as e:
        logger.error(f"Failed to start CV pipeline: {e}")
        raise e

        raise e



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