from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from db.session import get_db
from models import AlertConfig, Class

router = APIRouter(
    prefix="/classes",
    tags=["alert-config"],
)


class AlertConfigOut(BaseModel):
    id:                   int
    class_id:             int
    absence_threshold:    float
    attention_threshold:  float
    recipient_emails:     List[str]

    class Config:
        from_attributes = True


class AlertConfigUpdate(BaseModel):
    absence_threshold:   Optional[float] = None
    attention_threshold: Optional[float] = None
    recipient_emails:    Optional[List[str]] = None


@router.get("/{class_id}/alert-config", response_model=AlertConfigOut)
def get_alert_config(
    class_id: int,
    db:       Session = Depends(get_db),
):
    # verify class exists
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class {class_id} not found",
        )

    config = db.query(AlertConfig).filter(
        AlertConfig.class_id == class_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No alert config for class {class_id}",
        )

    return config


@router.put("/{class_id}/alert-config", response_model=AlertConfigOut)
def update_alert_config(
    class_id: int,
    payload:  AlertConfigUpdate,
    db:       Session = Depends(get_db),
):
    # verify class exists
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class {class_id} not found",
        )

    config = db.query(AlertConfig).filter(
        AlertConfig.class_id == class_id
    ).first()

    # create if doesn't exist
    if not config:
        config = AlertConfig(
            class_id=class_id,
            absence_threshold=0.3,
            attention_threshold=0.4,
            recipient_emails=[],
        )
        db.add(config)

    # update only provided fields
    if payload.absence_threshold is not None:
        if not 0.0 <= payload.absence_threshold <= 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="absence_threshold must be between 0.0 and 1.0",
            )
        config.absence_threshold = payload.absence_threshold

    if payload.attention_threshold is not None:
        if not 0.0 <= payload.attention_threshold <= 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="attention_threshold must be between 0.0 and 1.0",
            )
        config.attention_threshold = payload.attention_threshold

    if payload.recipient_emails is not None:
        config.recipient_emails = payload.recipient_emails

    db.commit()
    db.refresh(config)
    return config