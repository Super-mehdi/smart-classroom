from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
import httpx

from db.session import get_db
from models import Student, User, UserRole
from schemas.students import StudentCreate, StudentUpdate, StudentResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/students", tags=["students"])

# Use an absolute path that we will mount in Docker
FACES_DIR = Path("/cv_worker/cv_absence/faces")
CV_SERVER_URL = "http://cv_server:5001"

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can manage students"
        )
    return current_user

async def trigger_cv_enrollment():
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{CV_SERVER_URL}/enroll")
    except Exception as e:
        print(f"Failed to trigger CV enrollment: {e}")

@router.get("", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Student).all()

@router.post("", response_model=StudentResponse)
async def create_student(
    student_id: str = Form(...),
    name: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)
):
    # Check if student exists
    existing = db.query(Student).filter(Student.id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # Save photo
    extension = os.path.splitext(photo.filename)[1].lower()
    if extension not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Use JPG or PNG.")
    
    filename = f"{student_id}_{name}{extension}"
    target_path = FACES_DIR / filename
    
    # Ensure directory exists
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    
    new_student = Student(
        id=student_id,
        name=name,
        photo_path=str(target_path)
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # Trigger enrollment
    await trigger_cv_enrollment()
    
    return new_student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    name: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    changed = False
    if name and name != student.name:
        # If name changes, we might need to rename the file
        if student.photo_path:
            old_path = Path(student.photo_path)
            if old_path.exists():
                extension = old_path.suffix
                new_filename = f"{student_id}_{name}{extension}"
                new_path = FACES_DIR / new_filename
                old_path.rename(new_path)
                student.photo_path = str(new_path)
        student.name = name
        changed = True
    
    if photo:
        # Delete old photo if it exists
        if student.photo_path:
            old_p = Path(student.photo_path)
            if old_p.exists():
                old_p.unlink()
        
        extension = os.path.splitext(photo.filename)[1].lower()
        filename = f"{student_id}_{student.name}{extension}"
        target_path = FACES_DIR / filename
        
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        student.photo_path = str(target_path)
        changed = True

    db.commit()
    db.refresh(student)
    
    if changed:
        await trigger_cv_enrollment()
        
    return student

@router.delete("/{student_id}")
async def delete_student(student_id: str, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete photo file
    if student.photo_path:
        p = Path(student.photo_path)
        if p.exists():
            p.unlink()
    
    db.delete(student)
    db.commit()
    
    # Trigger enrollment to remove from mongo
    await trigger_cv_enrollment()
    
    return {"status": "ok"}
