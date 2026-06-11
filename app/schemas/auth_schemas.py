from pydantic import BaseModel, EmailStr, SecretStr, field_validator, TypeAdapter
import re

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9._-]{1,28}[a-zA-Z0-9])?$')
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr  # Protect the password from leaking

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password_raw = value.get_secret_value()

        if len(password_raw) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in password_raw):
            raise ValueError("Password must contain at least one number.")
        
        if not any(char.isupper() for char in password_raw):
            raise ValueError("Password must contain at least one uppercase letter.")

        return value
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not (3 <= len(value) <= 30):
            raise ValueError("Username must be between 3 and 30 characters long.")
        
        if not USERNAME_REGEX.match(value):
            raise ValueError("Username can contain letters, numbers, dots, underscores, and hyphens, and must start and end with a letter or number.")
        
        if ".." in value or "__" in value or "--" in value:
            raise ValueError("Username cannot contain consecutive dots, underscores, or hyphens.")
        
        return value.lower()  # Normalize username to lowercase

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    identifier: str  # Can be either username or email
    password: SecretStr

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v:str):
        v = v.strip()
        
        try:
            adapter = TypeAdapter(EmailStr)
            adapter.validate_python(v)
            return v.lower()
        except Exception:
            pass
        
        if not USERNAME_REGEX.match(v):
            raise ValueError("Enter a valid email or username")
        
        if ".." in v or "__" in v or "--" in v:
            raise ValueError("Username cannot contain consecutive dots, underscores, or hyphens.")
        
        return v.lower()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    
class RefreshIn(BaseModel):
    token: str