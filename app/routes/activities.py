from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.activity import ActivityLog
from app.schemas.activity import ActivityLogResponse
from typing import List

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.get("/", response_model=List[ActivityLogResponse])
def get_activities(organization_id: int, db: Session = Depends(get_db)):
    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.organization_id == organization_id)
        .order_by(ActivityLog.timestamp.desc())
        .all()
    )
    return activities