from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2)
    description: str | None = None
    assignee_id: Optional[int] = None    
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"

class TaskStatusUpdate(BaseModel):
    status: TaskStatus
