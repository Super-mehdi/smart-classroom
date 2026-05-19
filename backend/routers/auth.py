# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from core.dependencies import get_current_user
from db.session import get_db
from models import User
from schemas.auth import LoginRequest, TokenResponse
from core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Look up the user by email
    user = db.query(User).filter(User.email == payload.email).first()

    # 2. Verify — same error for both cases to avoid user enumeration
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Issue token — use email as the subject (or user.id if you prefer)
    token = create_access_token(subject=user.email)
    
    # 4. Mark as online and update last_seen
    user.is_online = True
    user.last_seen = datetime.utcnow()
    db.commit()
    
    return TokenResponse(access_token=token)

@router.post("/heartbeat")
def heartbeat(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.last_seen = datetime.utcnow()
    current_user.is_online = True
    db.commit()
    return {"status": "ok"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }

@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.is_online = False
    db.commit()
    return {"status": "ok"}