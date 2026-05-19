from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    department: Optional[str] = None
    office_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    office_number: Optional[str] = None
    password: Optional[str] = None
    is_online: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_online: bool

    class Config:
        from_attributes = True
