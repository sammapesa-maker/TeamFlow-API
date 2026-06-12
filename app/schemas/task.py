from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=30)
    description: Optional[str] = None

    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"

class TaskCreate(TaskBase):
    team_id: int = Field(..., gt=0)
    assigned_to_id: Optional[int] = Field(None, gt=0)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=30)
    description: Optional[str] = None

    status: Optional[Literal["todo", "in_progress", "done"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None

    assigned_to_id: Optional[int] = Field(None, gt=0)

class TaskRead(TaskBase):
    id: int
    team_id: int
    creator_id: int
    assigned_to_id: Optional[int]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Optional rich detailed taskread
class UserSimple(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TaskReadDetailed(TaskRead):
    creator: UserSimple
    assignee: Optional[UserSimple]