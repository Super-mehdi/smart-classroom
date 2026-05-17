from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from db.mongo import get_mongo_db

router = APIRouter(
    prefix="/sessions",
    tags=["alert-history"],
)


@router.get("/{session_id}/alert-history")
async def get_alert_history(session_id: int):
    db = get_mongo_db()

    docs = await db["alert_history"].find(
        {"session_id": session_id}
    ).sort("triggered_at", -1).to_list(length=100)

    # convert ObjectId and datetime to strings
    results = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("triggered_at"), datetime):
            doc["triggered_at"] = doc["triggered_at"].isoformat()
        results.append(doc)

    return {
        "session_id": session_id,
        "count":      len(results),
        "alerts":     results,
    }