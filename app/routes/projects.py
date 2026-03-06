from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.model import Project
from app.schemas.project import ProjectCreate
from app.core.permissions import require_org_role

router = APIRouter(prefix="/organizations/{org_id}/projects", tags=["projects"])

@router.post("/")
def create_project(
    org_id: int,
    data: ProjectCreate,
    db: Session = Depends(get_db),
    membership = Depends(require_org_role(["Admin"])),
):
    project = Project(
        name=data.name,
        description=data.description,
        organization_id=org_id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/")
def list_projects(
    org_id: int,
    db: Session = Depends(get_db),
    membership = Depends(require_org_role(["Admin", "Member", "Viewer"])),
):
    return (
        db.query(Project)
        .filter(Project.organization_id == org_id)
        .all()
    )


@router.get("/{project_id}")
def get_project(
    org_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    membership = Depends(require_org_role(["Admin", "Member", "Viewer"])),
):
    project = get_project_or_404(db, project_id, org_id)
    return project
