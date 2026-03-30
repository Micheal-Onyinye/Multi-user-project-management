from asyncio import tasks
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.model import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate
from app.core.permissions import require_org_role
from app.core.project_access import get_project_or_404
from app.core.activity_logger import log_activity
from app.core.actions import Actions
from app.core.auth import get_current_user
from app.models.model import User
from app.core.notify import create_notification
from app.core.task import update_task_status_if_overdue

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
    _ = Depends(require_org_role(["Admin", "Member"])),
    current_user: User = Depends(get_current_user)
):
    project = get_project_or_404(db, project_id, org_id)


    task = Task(
        title=data.title,
        description=data.description,
        project_id=project.id,
        assignee_id=data.assignee_id,
        due_date=data.due_date
    )
    
    log_activity(
    db=db,
    user_id=current_user.id,
    organization_id=org_id,
    action=Actions.CREATE_TASK,
    description=f"{current_user.email} created task '{task.title}'"
    )

    if task.assignee_id:
        create_notification(
        db=db,
        user_id=task.assignee_id,
        message=f"You were assigned a new task: {task.title}"
    )

    if task.assignee_id is not None:
        user = db.query(User).filter(User.id == task.assignee_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid assignee_id")
    
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
    _ = Depends(require_org_role(["Admin", "Member"]))    
):
    project = get_project_or_404(db, project_id, org_id)

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")


    task.status = data.status

    if data.status == "overdue":
        raise HTTPException(status_code=400, detail="Cannot manually set overdue")
    

    db.commit()
    db.refresh(task)

    return task



@router.patch("/{task_id}")
def update_task(
    org_id: int,
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_org_role(["Admin", "Member"])),
    current_user: User = Depends(get_current_user)
):
    project = get_project_or_404(db, project_id, org_id)

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title is not None:
        task.title = data.title

    if data.description is not None:
        task.description = data.description

    if data.assignee_id is not None:
        task.assignee_id = data.assignee_id

    log_activity(
    db=db,
    user_id=current_user.id,
    organization_id=org_id,
    action=Actions.UPDATE_TASK,
    description=f"{current_user.email} updated task '{task.title}'"
    )

    if task.assignee_id:
        create_notification(
        db=db,
        user_id=task.assignee_id,
        message=f" Task {task.title} was updated"
    )

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    org_id: int,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_org_role(["Admin", "Member"])),
    current_user: User = Depends(get_current_user)
):
    project = get_project_or_404(db, project_id, org_id)

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
   

    log_activity(
    db=db,
    user_id=current_user.id,
    organization_id=org_id,
    action=Actions.DELETE_TASK,
    description=f"{current_user.email} deleted task '{task.title}'"
    )

    if task.assignee_id:
        create_notification(
        db=db,
        user_id=task.assignee_id,
        message=f"Task {task.title} was deleted"
    )
   
    db.delete(task)
    db.commit()
    

    return ("Message: Task deleted successfully")


@router.get("/")
def get_tasks(
    org_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_org_role(["Admin", "Member"]))
):
    project = get_project_or_404(db, project_id, org_id)

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project.id)
        .all()
    )

    updated = False

    for task in tasks:
        old_status = task.status
        update_task_status_if_overdue(task)

        if task.status != old_status:
            updated = True

    if updated:
        db.commit()

    return tasks


@router.get("/{task_id}")
def get_task(
    org_id: int,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_org_role(["Admin", "Member"]))
):
    project = get_project_or_404(db, project_id, org_id)

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    
    old_status = task.status
    update_task_status_if_overdue(task)

    if task.status != old_status:
        db.commit()

    return task