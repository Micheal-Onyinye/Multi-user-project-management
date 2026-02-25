from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2)
    description: str | None = None
    assignee_id: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None