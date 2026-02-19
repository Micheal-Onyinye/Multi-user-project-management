from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Project

def get_project_or_404(
    db: Session,
    project_id: int,
    organization_id: int,
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project
