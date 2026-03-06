from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.models.model import Invitation, OrganizationMember, User
from app.schemas.invitation import InviteUserSchema, InvitationResponse
from app.core.auth import get_current_user
from app.core.permissions import require_org_admin

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("/{organization_id}", response_model=InvitationResponse)
def invite_user(
    organization_id: int,
    data: InviteUserSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Admin check
    require_org_admin(db, organization_id, current_user.id)

    # 2. Prevent inviting existing members
    existing_member = db.query(OrganizationMember).join(User).filter(
        OrganizationMember.organization_id == organization_id,
        User.email == data.email
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to this organization"
        )

    # 3. Prevent duplicate pending invites
    existing_invite = db.query(Invitation).filter(
        Invitation.organization_id == organization_id,
        Invitation.email == data.email,
        Invitation.status == "pending"
    ).first()

    if existing_invite:
        raise HTTPException(
            status_code=400,
            detail="Invitation already sent"
        )

    # 4. Create invitation
    invite = Invitation(
        organization_id=organization_id,
        email=data.email,
        role=data.role
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    return invite


@router.get("/me")
def my_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invites = db.query(Invitation).filter(
        Invitation.email == current_user.email,
        Invitation.status == "pending"
    ).all()

    return invites


@router.post("/{invitation_id}/accept")
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invite = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.email == current_user.email,
        Invitation.status == "pending"
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invitation not found")

    # Add membership
    membership = OrganizationMember(
        organization_id=invite.organization_id,
        user_id=current_user.id,
        role=invite.role
    )
    db.add(membership)

    # Update invite
    invite.status = "accepted"
    invite.responded_at = datetime.utcnow()

    db.commit()

    return {"message": "Invitation accepted"}


@router.post("/{invitation_id}/reject")
def reject_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invite = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.email == current_user.email,
        Invitation.status == "pending"
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invitation not found")

    invite.status = "rejected"
    invite.responded_at = datetime.utcnow()

    db.commit()

    return {"message": "Invitation rejected"}
