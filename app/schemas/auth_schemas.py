from datetime import datetime
from enum import Enum
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

# -------------------------
# AUTH SCHEMAS
# -------------------------


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr
    
    # Username validation
    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if len(value) < 3 or len(value) > 20:
            raise ValueError("Username must be between 3 and 20 characters")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value

    # Password validation
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value


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
    created_at: datetime
    updated_at: datetime

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
    created_at = "created_at"
    updated_at = "updated_at"
    id_desc = "-id"
    username_desc = "-username"
    created_at_desc = "-created_at"
    updated_at_desc = "-updated_at"


class UserQueryParams(BaseModel):
    # Filtering fields
    username_contains: Optional[str] = Field(
        default=None,
        description="Case insensitive partial match on the username",
        max_length=255,
    )
    is_active: Optional[bool] = Field(
        default=None, description="Active or inactive filter"
    )
    is_superuser: Optional[bool] = Field(default=None, description="Super User filter")

    # Sorting fields
    sort_by: UserSortField = Field(
        default=UserSortField.id, description="Fields to sort by"
    )

    # --- Pagination fields ---
    limit: int = Field(
        default=20, ge=1, le=100, description="Number of records to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of records to skip")


class PaginatedUserResponse(BaseModel):
    """
    Always return metadata alongside results.
    Clients need to know total count for pagination UI.
    """

    total: int
    limit: int
    offset: int
    items: list[UserResponse]
