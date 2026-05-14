<<<<<<< HEAD
# backend/routers/attendance.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
=======
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
>>>>>>> feature/attention_tracker
from typing import List

from db.session import get_db
from models import AttendanceRecord, AttendanceStatus, Session as ClassSession

<<<<<<< HEAD
router = APIRouter(
    prefix="/api/sessions",
    tags=["attendance"],
)


class AttendanceBatch(BaseModel):
    present: List[str]   # list of student_id strings
    absent: List[str]
    timestamp: datetime = None


@router.post("/{session_id}/attendance", status_code=status.HTTP_201_CREATED)
def post_attendance(
    session_id: int,
    batch: AttendanceBatch,
    db: Session = Depends(get_db),
):
    # verify session exists
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    ts = batch.timestamp or datetime.now(timezone.utc)

    records = []
    for student_id in batch.present:
        records.append(AttendanceRecord(
            session_id=session_id,
            student_id=student_id,
            status=AttendanceStatus.present,
            timestamp=ts,
        ))
    for student_id in batch.absent:
        records.append(AttendanceRecord(
            session_id=session_id,
            student_id=student_id,
            status=AttendanceStatus.absent,
            timestamp=ts,
        ))

    db.add_all(records)
    db.commit()

    return {
        "session_id": session_id,
        "present":    len(batch.present),
        "absent":     len(batch.absent),
        "inserted":   len(records),
    }


@router.get("/{session_id}/attendance")
def get_attendance(
    session_id: int,
    db: Session = Depends(get_db),
):
    records = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.session_id == session_id)
        .order_by(AttendanceRecord.timestamp.desc())
        .all()
    )
    return [
        {
            "student_id": r.student_id,
            "status":     r.status,
            "timestamp":  r.timestamp,
        }
        for r in records
    ]
=======
router = APIRouter(prefix="/sessions", tags=["attendance"])


# ── Schemas ───────────────────────────────────────────

class AttendancePost(BaseModel):
    present:   List[str]        # list of student_ids present
    absent:    List[str]        # list of student_ids absent
    timestamp: datetime | None = None

class AttendanceRecordOut(BaseModel):
    id:         int
    session_id: int
    student_id: str
    status:     AttendanceStatus
    timestamp:  datetime

    class Config:
        from_attributes = True


# ── POST /sessions/{session_id}/attendance ────────────

@router.post("/{session_id}/attendance", response_model=List[AttendanceRecordOut])
def post_attendance(
    session_id: int,
    payload:    AttendancePost,
    db:         Session = Depends(get_db)
):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    ts      = payload.timestamp or datetime.utcnow()
    records = []

    all_students = {s: AttendanceStatus.present for s in payload.present}
    all_students.update({s: AttendanceStatus.absent for s in payload.absent})

    for student_id, status in all_students.items():
        record = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == student_id
        ).first()

        if record:
            record.status    = status
            record.timestamp = ts
        else:
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
    db:         Session = Depends(get_db)
):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    records = db.query(AttendanceRecord)\
        .filter(AttendanceRecord.session_id == session_id)\
        .order_by(AttendanceRecord.timestamp)\
        .all()

    return records
>>>>>>> feature/attention_tracker
