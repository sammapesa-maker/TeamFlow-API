from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
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


class TeamSortField(str, Enum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    id_desc = "-id"
    created_at_desc = "-created_at"
    updated_at_desc = "-updated_at"


class TeamQueryParams(BaseModel):
    # Filtering Fields
    name_contains: Optional[str] = Field(
        default=None, description="Partial match on the name of the team", max_length=30
    )
    owner_id: Optional[int] = Field(default=None, description="Team's owner id", ge=1)

    # Sorting Fields
    sort_by: TeamSortField = Field(default=TeamSortField.id)

    # Pagination Fields
    limit: int = Field(
        default=20, ge=1, le=100, description="Number of records to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of records to skip")


class PaginatedTeamResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TeamRead]
