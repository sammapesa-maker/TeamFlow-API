from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional

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
