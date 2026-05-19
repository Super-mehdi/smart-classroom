import os
import numpy as np
from deepface import DeepFace
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

MONGO_URI  = os.getenv("MONGO_URI")
MONGO_DB   = os.getenv("MONGO_DB")
FACES_DIR  = Path(__file__).parent / "faces"
MODEL_NAME = "ArcFace"

def get_collection():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]["face_embeddings"]

def enroll_all():
    if not FACES_DIR.exists():
        print(f"ERROR: faces/ folder not found at {FACES_DIR}")
        return

    photos = list(FACES_DIR.glob("*.jpg")) + list(FACES_DIR.glob("*.jpeg")) + list(FACES_DIR.glob("*.png"))
    if not photos:
        print("ERROR: No photos found in faces/ folder.")
        return

    col = get_collection()
    enrolled, skipped, failed = 0, 0, 0
    current_ids = []

    for photo in photos:
        stem  = photo.stem
        parts = stem.split("_", 1)
        if len(parts) != 2:
            print(f"SKIP: {photo.name} — filename must be S001_Mehdi.png format")
            skipped += 1
            continue

        student_id, name = parts[0], parts[1]
        current_ids.append(student_id)

        try:
            result    = DeepFace.represent(
                img_path   = str(photo),
                model_name = MODEL_NAME,
                enforce_detection = True
            )
            embedding = result[0]["embedding"]

            col.update_one(
                {"student_id": student_id},
                {"$set": {
                    "student_id": student_id,
                    "name":       name,
                    "embedding":  embedding,
                    "model":      MODEL_NAME,
                }},
                upsert=True
            )
            print(f"OK: {student_id} — {name}")
            enrolled += 1

        except Exception as e:
            print(f"FAIL: {photo.name} — {e}")
            failed += 1

    # Sync deletions: remove IDs that are in Mongo but NOT in the faces folder
    delete_result = col.delete_many({"student_id": {"$nin": current_ids}})
    if delete_result.deleted_count > 0:
        print(f"DELETED: {delete_result.deleted_count} stale students from database")

    print(f"\nDone. {enrolled} enrolled, {skipped} skipped, {failed} failed.")

if __name__ == "__main__":
    enroll_all()