from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from schemas.schemas import AttentionLogBatch
from db.mongo import get_mongo_db
from tasks.alert_tasks import check_attention_alert

router = APIRouter(
    prefix="/sessions",
    tags=["attention"],
)


@router.post(
    "/{session_id}/attention",
    status_code=status.HTTP_201_CREATED,
)
async def post_attention_logs(
    session_id: int,
    batch:      AttentionLogBatch,
):
    if not batch.logs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch cannot be empty",
        )

    db = get_mongo_db()

    documents = [
        {
            "session_id": session_id,
            "student_id": log.student_id,
            "score":      log.score,
            "yaw":        log.yaw,
            "pitch":      log.pitch,
            "ear":        log.ear,
            "ts":         log.timestamp,
        }
        for log in batch.logs
    ]

    result = await db["attention_logs"].insert_many(documents)

    # fire and forget — check attention threshold
    check_attention_alert.delay(session_id)

    return {
        "inserted":   len(result.inserted_ids),
        "session_id": session_id,
    }


@router.get("/{session_id}/attention/latest")
async def get_latest_attention(session_id: int):
    db     = get_mongo_db()
    now    = datetime.utcnow()
    cutoff = now - timedelta(seconds=10)

    pipeline = [
        {
            "$match": {
                "session_id": session_id,
                "ts": {"$gte": cutoff},
            }
        },
        {"$sort": {"ts": 1}},
        {
            "$group": {
                "_id":   "$student_id",
                "score": {"$last": "$score"},
                "yaw":   {"$last": "$yaw"},
                "pitch": {"$last": "$pitch"},
                "ear":   {"$last": "$ear"},
                "ts":    {"$last": "$ts"},
            }
        },
        {
            "$project": {
                "_id":        0,
                "student_id": "$_id",
                "score":      1,
                "yaw":        1,
                "pitch":      1,
                "ear":        1,
                "ts":         1,
            }
        },
        {"$sort": {"student_id": 1}},
    ]

    results = await db["attention_logs"].aggregate(pipeline).to_list(length=100)

    if not results:
        return {
            "session_id":  session_id,
            "window_secs": 10,
            "students":    [],
            "class_avg":   None,
        }

    scores    = [r["score"] for r in results]
    class_avg = round(sum(scores) / len(scores), 4)

    return {
        "session_id":  session_id,
        "window_secs": 10,
        "students":    results,
        "class_avg":   class_avg,
    }