from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=30)
    description: Optional[str] = None
    status: Literal["todo", "progress", "done"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=30)
    description: Optional[str] = None
    status: Optional[Literal["todo", "progress", "done"]] = None
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


class TaskStatusEnum(str, Enum):
    todo = "todo"
    progress = "progress"
    done = "done"

class TaskPriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskSortField(str, Enum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    id_desc = "-id"
    created_at_desc = "-created_at"
    updated_at_desc = "-updated_at"
    title_desc = "-title"


class TaskQueryParams(BaseModel):
    # Filtering Fields
    title_contains: Optional[str] = Field(
        default=None, description="Partial match on the title of the Task", max_length=30
    )
    creator_id: Optional[int] = Field(default=None, description="Task's creator id", ge=1)
    team_id: Optional[int] = Field(default=None, description="Task's team id", ge=1)
    assigned_to_id: Optional[int] = Field(default=None, description="Task's assigned to id", ge=1)
    status: Optional[TaskStatusEnum] = Field(default=None, description="Current status of the task")
    priority: Optional[TaskPriorityEnum] = Field(default=None, description="Priority of the task")

    # Sorting Fields
    sort_by: TaskSortField = Field(default=TaskSortField.id)

    # Pagination Fields
    limit: int = Field(
        default=20, ge=1, le=100, description="Number of records to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of records to skip")


class PaginatedTaskResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TaskRead]
