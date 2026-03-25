from sqlalchemy.orm import Session
from app.models.activity import ActivityLog

def log_activity(
    db: Session,
    user_id: int,
    organization_id: int,
    action: str,
    description: str
):
    activity = ActivityLog(
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        description=description
    )

    db.add(activity)
    db.commit()