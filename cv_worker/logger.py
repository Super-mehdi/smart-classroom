import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB  = os.getenv("MONGO_DB")

_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = MongoClient(MONGO_URI)
        _collection = _client[MONGO_DB]["cv_debug_logs"]
    return _collection

def log_frame(session_id: int, frame_id: int, face_count: int, enrolled_count: int):
    """
    Write a debug entry to MongoDB cv_debug_logs collection.
    Matches the index: (session_id, frame_id)
    """
    doc = {
        "session_id":     session_id,
        "frame_id":       frame_id,
        "face_count":     face_count,
        "enrolled_count": enrolled_count,
        "absent_count":   max(0, enrolled_count - face_count),
        "ts":             time.time(),
    }
    try:
        _get_collection().insert_one(doc)
    except Exception as e:
        print(f"WARNING: Failed to log to MongoDB: {e}")
