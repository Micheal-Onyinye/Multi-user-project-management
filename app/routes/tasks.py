from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.permissions import require_org_role
from app.core.project_access import get_project_or_404

router = APIRouter(
    prefix="/organizations/{org_id}/projects/{project_id}/tasks",
    tags=["tasks"]
)

@router.post("/")
def create_task(
    org_id: int,
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    membership = Depends(require_org_role(["Admin", "Member"])),
):
    project = get_project_or_404(db, project_id, org_id)

    task = Task(
        title=data.title,
        description=data.description,
        project_id=project.id,
        assignee_id=data.assignee_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task

  
@router.patch("/{task_id}/status")
def update_task_status(
    org_id: int,
    project_id: int,
    task_id: int,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    membership = Depends(require_org_role(["Admin", "Member"])),
):
    project = get_project_or_404(db, project_id, org_id)

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.status not in TASK_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid task status")

    allowed = ALLOWED_TRANSITIONS.get(task.status, [])

    if data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move task from {task.status} to {data.status}"
        )

    task.status = data.status
    db.commit()
    db.refresh(task)
    return task