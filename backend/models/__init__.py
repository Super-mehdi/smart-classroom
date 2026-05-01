import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Enum, Boolean, ARRAY
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class UserRole(str, enum.Enum):
    teacher   = "teacher"
    superuser = "superuser"


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent  = "absent"


# ── User ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.teacher)
    created_at = Column(DateTime, default=datetime.utcnow)

    # one teacher → many classes
    classes = relationship("Class", back_populates="teacher")


# ── Class ─────────────────────────────────────────────

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="classes")
    sessions = relationship("Session", back_populates="class_")
    alert_config = relationship("AlertConfig", back_populates="class_", uselist=False)


# ── Session ───────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)   # null = still live

    class_ = relationship("Class", back_populates="sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="session")


# ── AttendanceRecord ──────────────────────────────────

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    student_id = Column(String, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="attendance_records")


# ── AlertConfig ───────────────────────────────────────

class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, unique=True)
    absence_threshold = Column(Float, default=0.3)   # 30% absent → alert
    attention_threshold = Column(Float, default=0.4)   # avg score below 0.4 → alert
    recipient_emails = Column(ARRAY(String), default=[])

    class_ = relationship("Class", back_populates="alert_config")