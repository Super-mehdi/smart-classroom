from pydantic import BaseModel

class ClassResponse(BaseModel):
    id: int
    name: str
    teacher_id: int

    class Config:
        from_attributes = True
