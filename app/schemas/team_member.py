from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TeamMemberBase(BaseModel):
    role: Literal["owner", "admin", "member"] = "member"
    status: Literal["invited", "active", "removed"] = "invited"


class TeamMemberCreate(TeamMemberBase):
    user_id: int = Field(..., gt=0)


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


class TeamMemberRoleEnum(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class TeamMemberStatusEnum(str, Enum):
    invited = "invited"
    active = "active"
    removed = "removed"


class TeamMemberSortField(str, Enum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    id_desc = "-id"
    created_at_desc = "-created_at"
    updated_at_desc = "-updated_at"


class TeamMemberQueryParams(BaseModel):
    # Filtering Fields
    user_id: Optional[int] = Field(default=None, description="Filter by user id", ge=1)
    team_id: Optional[int] = Field(default=None, description="Filter by team id", ge=1)
    role: Optional[TeamMemberRoleEnum] = Field(
        default=None, description="Filter by membership role"
    )
    status: Optional[TeamMemberStatusEnum] = Field(
        default=None, description="Filter by member status"
    )

    # Sorting Fields
    sort_by: TeamMemberSortField = Field(default=TeamMemberSortField.id)

    # Pagination Fields
    limit: int = Field(
        default=20, ge=1, le=100, description="Number of records to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of records to skip")


class PaginatedTeamMemberResponse(BaseModel):
    """
    Always return metadata alongside results.
    Clients need to know total count for pagination UI.
    """

    total: int
    limit: int
    offset: int
    items: list[TeamMemberRead]
