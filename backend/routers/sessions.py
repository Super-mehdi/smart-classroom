import logging
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from db.session import get_db
from db.mongo import get_mongo_db
from models import User, Session as SessionModel, Class, Student, AttendanceRecord, AttendanceStatus
from core.dependencies import get_current_user, require_teacher
from schemas.sessions import (
    SessionStartRequest, SessionResponse, SessionStopResponse, 
    SessionListItem, SessionSummaryResponse
)
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/start", response_model=SessionResponse)
def start_session(
    payload: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    # Verify class exists and belongs to teacher (unless superuser)
    course = db.query(Class).filter(Class.id == payload.class_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if current_user.role != "superuser" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your class")

    new_session = SessionModel(
        class_id=payload.class_id,
        started_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id}

@router.post("/{session_id}/stop", response_model=SessionStopResponse)
def stop_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    session_record = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    course = db.query(Class).filter(Class.id == session_record.class_id).first()
    if current_user.role != "superuser" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    session_record.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session_record)
    return {
        "session_id": session_record.id,
        "ended_at": session_record.ended_at
    }

@router.get("", response_model=List[SessionListItem])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    query = db.query(SessionModel).join(Class)
    
    if current_user.role != "superuser":
        query = query.filter(Class.teacher_id == current_user.id)
    
    sessions = query.all()
    
    # Map to schema
    return [
        SessionListItem(
            session_id=s.id,
            class_id=s.class_id,
            class_name=s.class_.name,
            started_at=s.started_at,
            ended_at=s.ended_at
        ) for s in sessions
    ]

@router.post("/{session_id}/cv/start")
def start_cv(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    session_record = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Ownership check
    course = db.query(Class).filter(Class.id == session_record.class_id).first()
    if current_user.role != "superuser" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    try:
        # Set session state in Redis so the CV worker process can see it immediately
        import redis
        import os
        r = redis.Redis.from_url(os.environ["CELERY_BROKER"], decode_responses=True)
        r.set("smartclass:session_id", session_id)
        r.delete("smartclass:attention_data")

        logger.info(f"Sending start_cv_pipeline task for session {session_id} to queue cv_worker")
        celery_app.send_task("tasks.start_cv_pipeline", queue="cv_worker")
    except Exception as e:
        logger.error(f"Failed to start CV for session {session_id}: {e}")
        return {"status": "cv_start_failed", "error": str(e)}
    return {"status": "cv_started"}

@router.post("/{session_id}/cv/stop")
def stop_cv(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    session_record = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Ownership check
    course = db.query(Class).filter(Class.id == session_record.class_id).first()
    if current_user.role != "superuser" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    try:
        # Clear session state in Redis
        import redis
        import os
        r = redis.Redis.from_url(os.environ["CELERY_BROKER"], decode_responses=True)
        r.delete("smartclass:session_id")
        r.delete("smartclass:attention_data")

        logger.info(f"Sending stop_cv_pipeline task for session {session_id} to queue cv_worker")
        celery_app.send_task("tasks.stop_cv_pipeline", queue="cv_worker")
    except Exception as e:
        logger.error(f"Failed to stop CV for session {session_id}: {e}")
        return {"status": "cv_stop_failed", "error": str(e)}
    return {"status": "cv_stopped"}

@router.post("/{session_id}/summary", response_model=SessionSummaryResponse)
async def generate_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    # 1. Check if summary already exists
    mongo_db = get_mongo_db()
    existing_summary = await mongo_db["session_summaries"].find_one({"session_id": session_id})
    if existing_summary:
        return {
            "session_id": existing_summary["session_id"],
            "summary_text": existing_summary["summary_text"],
            "stats": existing_summary["stats"],
            "generated_at": existing_summary["generated_at"]
        }

    # 2. Verify session exists
    session_record = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")

    # 3. Compute stats
    # Attention stats from MongoDB
    attn_pipeline = [
        {"$match": {"session_id": session_id}},
        {"$group": {
            "_id": None,
            "avg_score": {"$avg": "$score"}
        }}
    ]
    attn_results = await mongo_db["attention_logs"].aggregate(attn_pipeline).to_list(length=1)
    avg_attention = round(attn_results[0]["avg_score"], 4) if attn_results and attn_results[0]["avg_score"] is not None else 0

    # Attendance stats from PostgreSQL
    total_enrolled = db.query(Student).count()
    present_count = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id,
        AttendanceRecord.status == AttendanceStatus.present
    ).count()
    attendance_rate = round((present_count / total_enrolled) * 100, 2) if total_enrolled > 0 else 0

    stats = {
        "avg_attention": avg_attention,
        "attendance_rate": attendance_rate,
        "present_students": present_count,
        "total_students": total_enrolled
    }

    # 4. Call Groq API
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    prompt = f"""
    Please provide a concise and professional summary of the following classroom session for the teacher.
    
    Session ID: {session_id}
    Average Attention Score: {avg_attention} (out of 1.0)
    Attendance Rate: {attendance_rate}% ({present_count}/{total_enrolled} students present)
    
    The summary should highlight the overall engagement and attendance, and provide any general pedagogical advice based on these numbers.
    """

    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful educational assistant providing session summaries for teachers."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Calling Groq API for session {session_id}")
            response = await client.post(groq_url, headers=headers, json=payload, timeout=30.0)
            if response.status_code != 200:
                error_data = response.json()
                msg = error_data.get("error", {}).get("message", "Unknown Groq error")
                logger.error(f"Groq API returned {response.status_code}: {msg}")
                # Fallback to a smaller model if 70b fails or is unavailable
                logger.info("Retrying with llama-3.1-8b-instant...")
                payload["model"] = "llama-3.1-8b-instant"
                response = await client.post(groq_url, headers=headers, json=payload, timeout=30.0)
                if response.status_code != 200:
                    raise Exception(f"Groq primary and fallback failed. Last error: {msg}")
            
            response.raise_for_status()
            data = response.json()
            summary_text = data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Groq API call failed for session {session_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate summary with Groq: {str(e)}")

    # 5. Store in MongoDB
    generated_at = datetime.utcnow()
    summary_doc = {
        "session_id": session_id,
        "summary_text": summary_text,
        "stats": stats,
        "generated_at": generated_at
    }
    await mongo_db["session_summaries"].insert_one(summary_doc)

    return {
        "session_id": session_id,
        "summary_text": summary_text,
        "stats": stats,
        "generated_at": generated_at
    }
