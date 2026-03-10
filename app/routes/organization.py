from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.model import Organization, OrganizationMember, User, Role
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.core.auth import get_current_user
from app.schemas.organization_member import AddMemberSchema, OrganizationMemberResponse
from app.core.permissions import require_org_admin,require_org_role


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check if organization name already exists
    existing = db.query(Organization).filter(Organization.name == org_data.name).first()
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

    # 3. Ensure 'admin' role exists
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Organization administrator")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    # 4. Assign creator as admin
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role_id=admin_role.id
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

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

    role = db.query(Role).filter(Role.name == data.role).first()
    if not role:
            raise HTTPException(
        status_code=400,
        detail=f"Role '{data.role}' does not exist"
    )

    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role=role  # now this is a Role object
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
