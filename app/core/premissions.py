from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import OrganizationMember

def require_org_admin(
    db: Session,
    organization_id: int,
    user_id: int
):
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id
    ).first()

    if not membership or membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
