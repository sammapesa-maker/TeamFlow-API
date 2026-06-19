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
