from pydantic import BaseModel, EmailStr, SecretStr, field_validator, TypeAdapter
from typing import Optional
import re

# -------------------------
# CONSTANTS / HELPERS
# -------------------------

USERNAME_REGEX = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]{1,28}[a-zA-Z0-9])?$"
)


def validate_username(value: str) -> str:
    value = value.strip().lower()

    if not (3 <= len(value) <= 30):
        raise ValueError("Username must be between 3 and 30 characters long.")

    if not USERNAME_REGEX.match(value):
        raise ValueError(
            "Username can contain letters, numbers, dots, underscores, and hyphens, "
            "and must start and end with a letter or number."
        )

    if any(x in value for x in ["..", "__", "--"]):
        raise ValueError(
            "Username cannot contain consecutive dots, underscores, or hyphens."
        )

    return value


def validate_password(value: SecretStr) -> SecretStr:
    raw = value.get_secret_value()

    if len(raw) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    if not any(c.isdigit() for c in raw):
        raise ValueError("Password must contain at least one number.")

    if not any(c.isupper() for c in raw):
        raise ValueError("Password must contain at least one uppercase letter.")
    
    if not any(c.islower() for c in raw):
        raise ValueError("Password must contain a lowercase letter.")

    if not any(c in "!@#$%^&*" for c in raw):
        raise ValueError("Password must contain a special character.")

    return value


# -------------------------
# AUTH SCHEMAS
# -------------------------

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr

    _validate_username = field_validator("username")(validate_username)
    _validate_password = field_validator("password")(validate_password)


class UserLogin(BaseModel):
    identifier: str  # email or username
    password: SecretStr

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        v = v.strip().lower()

        # Try email
        try:
            TypeAdapter(EmailStr).validate_python(v)
            return v
        except Exception:
            pass

        # Fallback to username validation
        return validate_username(v)


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

    @field_validator("username")
    @classmethod
    def validate_username_optional(cls, v: Optional[str]):
        if v is None:
            return v
        return validate_username(v)


class ChangePassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr

    _validate_new_password = field_validator("new_password")(validate_password)