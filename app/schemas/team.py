from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TeamBase(BaseModel):
    name: str = Field(...,min_length=1, max_length=30)
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    description: Optional[str] = None

class TeamRead(TeamBase):
    id: int
    owner_id: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Optional detailed schema for rich responses
class UserSimple(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TeamMemberSimple(BaseModel):
    user_id: int
    role: str
    status: str

    class Config:
        from_attributes = True


class TeamReadDetailed(TeamRead):
    owner: UserSimple
    members: list[TeamMemberSimple] = []

# Optional with tasks
class TaskSimple(BaseModel):
    id: int
    title: str
    status: str

    class Config:
        from_attributes = True


class TeamReadWithTasks(TeamReadDetailed):
    tasks: list[TaskSimple] = []