from pydantic import BaseModel, EmailStr, SecretStr, Field
from typing import Optional
from enum import Enum

# -------------------------
# AUTH SCHEMAS
# -------------------------

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr


class UserLogin(BaseModel):
    identifier: str  # email or username
    password: SecretStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenIn(BaseModel):
    token: str


# -------------------------
# USER SCHEMAS
# -------------------------

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr

class UserSortField(str, Enum):
    id = "id"
    username = "username"
    created_at = "created-at"
    updated_at = "updated-at"
    id_desc = "-id"
    username_desc = "-username"
    created_at_desc = "-created-at"
    updated_at_desc = "-updated-at"

class UserQueryParams(BaseModel):
    # Filtering fields
    username_contains: Optional[str] = Field(
        default=None,
        description="Case insensitive partial match on the username",
        max_length=255
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Active or inactive filter"
    )
    is_superuser: Optional[bool] = Field(
        default=None,
        description="Super User filter"
    )
    
    # Sorting fields
    sort_by: UserSortField = Field(
        default=UserSortField.id,
        description="Fields to sort by"
    )
    
    # --- Pagination fields ---
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of records to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip"
    )

class PaginatedUserResponse(BaseModel):
    """
    Always return metadata alongside results.
    Clients need to know total count for pagination UI.
    """
    total: int
    limit: int
    offset: int
    items: list[UserResponse]