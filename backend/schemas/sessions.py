from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SessionStartRequest(BaseModel):
    class_id: int

class SessionResponse(BaseModel):
    session_id: int

class SessionStopResponse(BaseModel):
    session_id: int
    ended_at: datetime

class SessionListItem(BaseModel):
    session_id: int
    class_id: int
    class_name: str
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True
