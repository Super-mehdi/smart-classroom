import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from db.session import get_db
from models import User, Session as SessionModel, Class
from core.dependencies import get_current_user, require_teacher
from schemas.sessions import SessionStartRequest, SessionResponse, SessionStopResponse, SessionListItem
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
