from pydantic import BaseModel, EmailStr, SecretStr, field_validator

class UserRegister(BaseModel):
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

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr