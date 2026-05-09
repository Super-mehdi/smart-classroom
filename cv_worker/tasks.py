import os
import httpx
from celery_app import celery_app
import state

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


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
        print(f"Failed to post attention batch: {e}")