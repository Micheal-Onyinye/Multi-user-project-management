from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models import OrganizationMember
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models import User

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




def require_org_role(required_roles: list[str]):
    def checker(
        org_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == current_user.id
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization"
            )

        if membership.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return membership

    return checker
