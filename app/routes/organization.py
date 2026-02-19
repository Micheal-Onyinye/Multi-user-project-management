from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Organization, OrganizationMember, User
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.core.auth import get_current_user
from app.schemas.organization_member import AddMemberSchema, OrganizationMemberResponse
from app.core.permissions import require_org_admin


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    existing = db.query(Organization).filter(
        Organization.name == org_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Organization with this name already exists"
        )

    # 2. Create organization
    organization = Organization(
        name=org_data.name,
        owner_id=current_user.id
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)

    # 3. Creator becomes admin
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(membership)
    db.commit()

    return organization


@router.post("/{organization_id}/members",  response_model=OrganizationMemberResponse)
def add_member(
    organization_id: int,
    data: AddMemberSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Admin check
    require_org_admin(db, organization_id, current_user.id)

    # 2. Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email does not exist"
        )

    # 3. Prevent duplicate membership
    existing = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to this organization"
        )

    # 4. Add member
    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role=data.role
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return {
        "user_email": user.email,
        "role": member.role
    }


@router.get("/organizations/{org_id}")
def get_organization(
    org_id: int,
    membership = Depends(require_org_role(["Admin", "Member"])),
    db: Session = Depends(get_db),
):
    return {"organization_id": org_id}
