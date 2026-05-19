from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models import User, UserRole
from schemas.users import UserCreate, UserUpdate, UserResponse
from core.security import hash_password
from core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can manage users"
        )
    return current_user

from datetime import datetime, timedelta

@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    # Automatically mark users as offline if they haven't been seen in 2 minutes
    heartbeat_threshold = datetime.utcnow() - timedelta(minutes=2)
    db.query(User).filter(User.last_seen < heartbeat_threshold, User.is_online == True).update({"is_online": False})
    db.commit()
    
    return db.query(User).all()

@router.post("", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        department=payload.department,
        office_number=payload.office_number,
        is_online=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = payload.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

from models import User, UserRole, Class, Session as ClassroomSession, AttendanceRecord, AlertConfig

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Manually handle cascade
    classes = db.query(Class).filter(Class.teacher_id == user_id).all()
    for cls in classes:
        # 1. Delete alert configs
        db.query(AlertConfig).filter(AlertConfig.class_id == cls.id).delete()
        
        # 2. Get sessions
        sessions = db.query(ClassroomSession).filter(ClassroomSession.class_id == cls.id).all()
        for sess in sessions:
            # 3. Delete attendance records
            db.query(AttendanceRecord).filter(AttendanceRecord.session_id == sess.id).delete()
            db.delete(sess)
        
        db.delete(cls)
    
    db.delete(user)
    db.commit()
    return {"status": "ok"}
