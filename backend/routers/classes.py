from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from models import User, Class, UserRole
from core.dependencies import require_teacher
from schemas.classes import ClassResponse

router = APIRouter(tags=['classes'])

@router.get('/classes', response_model=List[ClassResponse])
def get_teacher_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    if current_user.role == UserRole.superuser:
        classes = db.query(Class).all()
    else:
        classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
    return classes
