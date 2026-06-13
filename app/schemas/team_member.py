from datetime import datetime
from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class TeamMemberBase(BaseModel):
    role: Literal["owner", "admin", "member"] = "member"
    status: Literal["invited", "active", "removed"] = "invited"

class TeamMemberCreate(TeamMemberBase):
    user_id: int = Field(..., gt=0)
    team_id: int = Field(..., gt=0)
    
class TeamMemberUpdate(BaseModel):
    role: Optional[Literal["owner", "admin", "member"]] = None
    status: Optional[Literal["invited", "active", "removed"]] = None

class TeamMemberRead(TeamMemberBase):
    id: int
    user_id: int
    team_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Optional detailed schemas for rich responses
class UserSimple(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TeamSimple(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TeamMemberReadDetailed(TeamMemberRead):
    user: UserSimple
    team: TeamSimple