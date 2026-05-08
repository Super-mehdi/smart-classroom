from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List

from db.session import get_db
from models import AttendanceRecord, AttendanceStatus, Session as ClassSession

router = APIRouter(prefix="/sessions", tags=["attendance"])


# ── Schemas ───────────────────────────────────────────

class AttendancePost(BaseModel):
    face_count: int          # number of persons detected by CV worker
    enrolled_count: int      # total students enrolled in this session
    timestamp: datetime | None = None

class AttendanceRecordOut(BaseModel):
    id: int
    session_id: int
    student_id: str
    status: AttendanceStatus
    timestamp: datetime

    class Config:
        from_attributes = True


# ── POST /sessions/{session_id}/attendance ────────────

@router.post("/{session_id}/attendance", response_model=List[AttendanceRecordOut])
def post_attendance(
    session_id: int,
    payload: AttendancePost,
    db: Session = Depends(get_db)
):
    # Make sure the session exists
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    ts = payload.timestamp or datetime.utcnow()
    face_count = max(0, min(payload.face_count, payload.enrolled_count))
    records = []

    for i in range(1, payload.enrolled_count + 1):
        student_id = f"student_{i}"
        status = AttendanceStatus.present if i <= face_count else AttendanceStatus.absent

        record = AttendanceRecord(
            session_id=session_id,
            student_id=student_id,
            status=status,
            timestamp=ts,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for r in records:
        db.refresh(r)

    return records


# ── GET /sessions/{session_id}/attendance ─────────────

@router.get("/{session_id}/attendance", response_model=List[AttendanceRecordOut])
def get_attendance(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    records = db.query(AttendanceRecord)\
        .filter(AttendanceRecord.session_id == session_id)\
        .order_by(AttendanceRecord.timestamp)\
        .all()

    return records