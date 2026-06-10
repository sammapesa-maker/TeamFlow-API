from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import create_user, get_user_by_email


def register_user(user_data: UserRegister, db: Session):
    # Check if user already exists
    if get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    try:
        user = create_user(user_data.email, hash_password(user_data.password.get_secret_value()), db)
        return user

    except Exception as e:  # Any unhandled exceptions during user creation
        print(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration",
        )


def login_user(user_data: UserLogin, db: Session):
    user = get_user_by_email(user_data.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(user_data.password.get_secret_value(), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # create and return access and refresh tokens
    return user
