from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# attention_logs
class AttentionLog(BaseModel):
    session_id: int
    student_id: str              
    score: float        
    yaw: float         
    pitch: float    
    ear: float                   
    ts: datetime = Field(default_factory=datetime.utcnow)


# cv_debug_logs
class CvDebugLog(BaseModel):
    session_id: int
    frame_id: int               
    bboxes: List[List[float]]    
    landmarks: List[List[float]] 
    ts: datetime = Field(default_factory=datetime.utcnow)


# alert_history
class AlertHistory(BaseModel):
    session_id: int
    type: str                    # "absence" or "attention"
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    payload: dict                # extra info e.g. {"absent_count": 5, "threshold": 0.3}


# face_embeddings
class FaceEmbedding(BaseModel):
    student_id: str              # e.g. "S042"
    embedding: List[float]       # 512 floats from the face recognition model
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)