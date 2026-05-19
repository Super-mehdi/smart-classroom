from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentBase(BaseModel):
    id: str
    name: str

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None

class StudentResponse(StudentBase):
    photo_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
