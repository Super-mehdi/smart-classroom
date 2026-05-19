import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from db.mongo import get_mongo_db
from models import (
    AttendanceRecord, AttendanceStatus,
    Session as ClassSession, Class, User, UserRole
)
from core.dependencies import get_current_user
import io
import csv
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/analytics", tags=["analytics"])


# ── 1. GET /analytics/sessions/{id} ──────────────────────
@router.get("/sessions/{session_id}")
async def get_session_analytics(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # verify session exists
    session = db.query(ClassSession).filter(
        ClassSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # ── attendance from PostgreSQL ────────────────────────
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id
    ).all()

    total    = len(records)
    present  = sum(1 for r in records if r.status == AttendanceStatus.present)
    absent   = total - present
    att_rate = round(present / total, 4) if total > 0 else None

    # ── attention per minute from MongoDB ─────────────────
    mongo_db = get_mongo_db()
    pipeline = [
        {"$match": {"session_id": session_id}},
        {
            "$group": {
                "_id": {
                    "$subtract": [
                        {"$toLong": "$ts"},
                        {"$mod": [{"$toLong": "$ts"}, 60000]}
                    ]
                },
                "avg_score": {"$avg": "$score"},
                "count":     {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id":       0,
                "minute_ts": "$_id",
                "avg_score": {"$round": ["$avg_score", 4]},
                "count":     1,
            }
        },
    ]

    attention_timeline = await mongo_db["attention_logs"].aggregate(
        pipeline
    ).to_list(length=1000)

    overall_avg = None
    if attention_timeline:
        overall_avg = round(
            sum(b["avg_score"] for b in attention_timeline) /
            len(attention_timeline), 4
        )

    return {
        "session_id":        session_id,
        "class_id":          session.class_id,
        "started_at":        session.started_at,
        "ended_at":          session.ended_at,
        "attendance": {
            "total":   total,
            "present": present,
            "absent":  absent,
            "rate":    att_rate,
        },
        "attention": {
            "overall_avg": overall_avg,
            "timeline":    attention_timeline,
        },
    }


# ── 2. GET /analytics/classes/{id} ───────────────────────
@router.get("/classes/{class_id}")
async def get_class_analytics(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # verify teacher owns this class or is superuser
    if (current_user.role != UserRole.superuser and
            cls.teacher_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # get last 30 sessions
    sessions = db.query(ClassSession).filter(
        ClassSession.class_id == class_id
    ).order_by(ClassSession.started_at.desc()).limit(30).all()

    if not sessions:
        return {"class_id": class_id, "sessions": []}

    session_ids = [s.id for s in sessions]
    mongo_db    = get_mongo_db()

    # attendance per session from PostgreSQL
    attendance_map = {}
    for sid in session_ids:
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == sid
        ).all()
        total   = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.present)
        attendance_map[sid] = {
            "total":   total,
            "present": present,
            "rate":    round(present / total, 4) if total > 0 else None,
        }

    # avg attention per session from MongoDB
    pipeline = [
        {"$match": {"session_id": {"$in": session_ids}}},
        {
            "$group": {
                "_id":       "$session_id",
                "avg_score": {"$avg": "$score"},
            }
        },
    ]
    attention_results = await mongo_db["attention_logs"].aggregate(
        pipeline
    ).to_list(length=100)
    attention_map = {
        r["_id"]: round(r["avg_score"], 4)
        for r in attention_results
    }

    # join in Python
    result_sessions = []
    for s in sessions:
        att  = attendance_map.get(s.id, {})
        attn = attention_map.get(s.id)
        result_sessions.append({
            "session_id":    s.id,
            "started_at":    s.started_at,
            "ended_at":      s.ended_at,
            "attendance":    att,
            "avg_attention": attn,
        })

    return {
        "class_id":  class_id,
        "class_name": cls.name,
        "sessions":  result_sessions,
    }


# ── 3. GET /analytics/students/{id} ──────────────────────
@router.get("/students/{student_id}")
async def get_student_analytics(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mongo_db = get_mongo_db()

    # attendance from PostgreSQL
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id
    ).order_by(AttendanceRecord.timestamp.desc()).all()

    total    = len(records)
    present  = sum(1 for r in records if r.status == AttendanceStatus.present)
    att_rate = round(present / total, 4) if total > 0 else None

    # attention trend from MongoDB — avg per session
    pipeline = [
        {"$match": {"student_id": student_id}},
        {
            "$group": {
                "_id":       "$session_id",
                "avg_score": {"$avg": "$score"},
                "count":     {"$sum": 1},
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": 30},
        {
            "$project": {
                "_id":        0,
                "session_id": "$_id",
                "avg_score":  {"$round": ["$avg_score", 4]},
                "count":      1,
            }
        },
    ]

    attention_per_session = await mongo_db["attention_logs"].aggregate(
        pipeline
    ).to_list(length=30)

    overall_avg = None
    trend       = None
    if attention_per_session:
        scores      = [s["avg_score"] for s in attention_per_session]
        overall_avg = round(sum(scores) / len(scores), 4)

        # trend: compare last 5 sessions vs previous 5
        if len(scores) >= 10:
            recent   = sum(scores[:5])  / 5
            previous = sum(scores[5:10]) / 5
            trend    = round(recent - previous, 4)

    return {
        "student_id": student_id,
        "attendance": {
            "total":   total,
            "present": present,
            "absent":  total - present,
            "rate":    att_rate,
        },
        "attention": {
            "overall_avg":        overall_avg,
            "trend":              trend,
            "per_session":        attention_per_session,
        },
    }


# ── 4. GET /analytics/overview (superuser only) ───────────
@router.get("/overview")
async def get_overview_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )

    mongo_db = get_mongo_db()
    classes  = db.query(Class).all()

    # avg attention per class from MongoDB
    pipeline = [
        {
            "$lookup": {
                "from":         "sessions",
                "localField":   "session_id",
                "foreignField": "id",
                "as":           "session",
            }
        },
        {
            "$group": {
                "_id":       "$session_id",
                "avg_score": {"$avg": "$score"},
            }
        },
    ]

    # simpler approach — get avg attention per session then map to class
    all_sessions = db.query(ClassSession).all()
    session_to_class = {s.id: s.class_id for s in all_sessions}
    session_ids = [s.id for s in all_sessions]

    attn_pipeline = [
        {"$match": {"session_id": {"$in": session_ids}}},
        {
            "$group": {
                "_id":       "$session_id",
                "avg_score": {"$avg": "$score"},
            }
        },
    ]
    attn_results = await mongo_db["attention_logs"].aggregate(
        attn_pipeline
    ).to_list(length=1000)

    # group by class
    class_attention: dict[int, list] = {}
    for r in attn_results:
        class_id = session_to_class.get(r["_id"])
        if class_id:
            class_attention.setdefault(class_id, []).append(r["avg_score"])

    result_classes = []
    for cls in classes:
        teacher = db.query(User).filter(User.id == cls.teacher_id).first()

        # attendance rate for this class
        class_sessions = [s for s in all_sessions if s.class_id == cls.id]
        class_sids     = [s.id for s in class_sessions]
        records        = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(class_sids)
        ).all()
        total   = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.present)

        # avg attention for this class
        scores    = class_attention.get(cls.id, [])
        avg_attn  = round(sum(scores) / len(scores), 4) if scores else None

        result_classes.append({
            "class_id":        cls.id,
            "class_name":      cls.name,
            "teacher":         teacher.full_name if teacher else None,
            "session_count":   len(class_sessions),
            "attendance_rate": round(present / total, 4) if total > 0 else None,
            "avg_attention":   avg_attn,
        })

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "classes":      result_classes,
    }

@router.get("/classes/{class_id}/export")
async def export_class_analytics(
    class_id: int,
    format: str = "csv",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if (current_user.role != UserRole.superuser and
            cls.teacher_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    mongo_db = get_mongo_db()

    # get all sessions for this class
    sessions = db.query(ClassSession).filter(
        ClassSession.class_id == class_id
    ).order_by(ClassSession.started_at.desc()).limit(30).all()

    session_ids = [s.id for s in sessions]
    session_map = {s.id: s for s in sessions}

    # attendance per session from PostgreSQL
    attendance_map = {}
    for sid in session_ids:
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == sid
        ).all()
        total   = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.present)
        attendance_map[sid] = {
            "total":   total,
            "present": present,
            "absent":  total - present,
            "rate":    round(present / total, 4) if total > 0 else None,
        }

    # avg attention per session from MongoDB
    pipeline = [
        {"$match": {"session_id": {"$in": session_ids}}},
        {
            "$group": {
                "_id":       "$session_id",
                "avg_score": {"$avg": "$score"},
                "min_score": {"$min": "$score"},
                "max_score": {"$max": "$score"},
            }
        },
    ]
    attn_results = await mongo_db["attention_logs"].aggregate(
        pipeline
    ).to_list(length=100)
    attention_map = {
        r["_id"]: {
            "avg": round(r["avg_score"], 4),
            "min": round(r["min_score"], 4),
            "max": round(r["max_score"], 4),
        }
        for r in attn_results
    }

    # merge into rows
    rows = []
    for sid in session_ids:
        s    = session_map[sid]
        att  = attendance_map.get(sid, {})
        attn = attention_map.get(sid, {})
        rows.append({
            "session_id":        sid,
            "started_at":        s.started_at.isoformat() if s.started_at else "",
            "ended_at":          s.ended_at.isoformat() if s.ended_at else "",
            "total_students":    att.get("total", 0),
            "present":           att.get("present", 0),
            "absent":            att.get("absent", 0),
            "attendance_rate":   att.get("rate", ""),
            "avg_attention":     attn.get("avg", ""),
            "min_attention":     attn.get("min", ""),
            "max_attention":     attn.get("max", ""),
        })

    # generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys() if rows else [])
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    filename = f"class_{class_id}_analytics.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )