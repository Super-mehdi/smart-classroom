from fastapi import APIRouter, Depends
from db.mongo import get_mongo_db
from core.dependencies import get_current_user

router = APIRouter(prefix="/students", tags=["students"])

@router.get("")
async def list_students(
    current_user=Depends(get_current_user)
):
    mongo_db = get_mongo_db()
    cursor = mongo_db["face_embeddings"].find({}, {"student_id": 1, "name": 1, "_id": 0})
    students = await cursor.to_list(length=1000)
    
    # Map to expected frontend format
    return [{"id": s["student_id"], "name": s.get("name", s["student_id"])} for s in students]
