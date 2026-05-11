import os
import numpy as np
from deepface import DeepFace
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

MONGO_URI  = os.getenv("MONGO_URI")
MONGO_DB   = os.getenv("MONGO_DB")
MODEL_NAME = "ArcFace"
THRESHOLD  = 0.68  # ArcFace cosine distance threshold

_known_ids        = []
_known_names      = []
_known_embeddings = []

def load_embeddings():
    global _known_ids, _known_names, _known_embeddings

    client = MongoClient(MONGO_URI)
    docs   = list(client[MONGO_DB]["face_embeddings"].find({}))

    _known_ids        = [d["student_id"]        for d in docs]
    _known_names      = [d["name"]              for d in docs]
    _known_embeddings = [np.array(d["embedding"]) for d in docs]

    print(f"Loaded {len(docs)} enrolled student(s): {', '.join(_known_names)}")

def _cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recognize_frame(frame) -> dict:
    present_ids = set()

    try:
        results = DeepFace.represent(
            img_path          = frame,
            model_name        = MODEL_NAME,
            enforce_detection = True
        )

        for r in results:
            embedding = np.array(r["embedding"])
            distances = [_cosine_distance(embedding, k) for k in _known_embeddings]

            if not distances:
                continue

            best_idx = int(np.argmin(distances))
            if distances[best_idx] <= THRESHOLD:
                present_ids.add(_known_ids[best_idx])

    except Exception:
        # No face detected in frame
        pass

    present, absent = [], []
    for sid, name in zip(_known_ids, _known_names):
        entry = {"student_id": sid, "name": name}
        if sid in present_ids:
            present.append(entry)
        else:
            absent.append(entry)

    return {"present": present, "absent": absent}