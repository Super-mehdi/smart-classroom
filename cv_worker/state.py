import os
import json
import redis
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis.from_url(
    os.environ["CELERY_BROKER"],
    decode_responses=True
)

SESSION_KEY   = "smartclass:session_id"
ATTENTION_KEY = "smartclass:attention_data"


def set_session(session_id: int):
    r.set(SESSION_KEY, session_id)


def clear_session():
    r.delete(SESSION_KEY)
    r.delete(ATTENTION_KEY)


def get_session_id():
    val = r.get(SESSION_KEY)
    return int(val) if val else None


def is_active() -> bool:
    return r.exists(SESSION_KEY) == 1


def update(
    student_id: str,
    score: float,
    yaw: float,
    pitch: float,
    ear: float,
):
    entry = {
        "student_id": student_id,
        "score":      score,
        "yaw":        yaw,
        "pitch":      pitch,
        "ear":        ear,
        "timestamp":  datetime.utcnow().isoformat(),
    }
    r.hset(ATTENTION_KEY, student_id, json.dumps(entry))


def get_and_clear() -> list:
    all_data = r.hgetall(ATTENTION_KEY)
    if not all_data:
        return []
    r.delete(ATTENTION_KEY)
    return [json.loads(v) for v in all_data.values()]