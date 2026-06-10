from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from datetime import datetime, timedelta, timezone
from app.repositories.user_repository import create_user, get_user_by_email
from app.core.config import get_settings
from jose import JWTError, jwt
from app.core.security import verify_token
from app.repositories.token_repository import get_refresh_token_by_jti, revoke_refresh_token, create_refresh_token_entry

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


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
    
    access_token = create_access_token(user.id)
    refresh_token, jti = create_refresh_token(user.id)

    create_refresh_token_entry(user.id, refresh_token, jti, datetime.now(timezone.utc) + timedelta(days=7), db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def refresh_token(token: str, db: Session):
    try:
        payload = jwt.decode(str(token), SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        print(f"Error : {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    user_id = payload.get("sub")

    db_token = get_refresh_token_by_jti(jti, db)

    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Token revoked")

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")

    if not verify_token(token, db_token.token_hash):
        raise HTTPException(status_code=401, detail="Token mismatch")

    # ROTATION: revoke old token
    revoke_refresh_token(jti, db)

    # Issue new tokens
    access_token = create_access_token(user_id)
    new_refresh_token, new_jti = create_refresh_token(user_id)

    create_refresh_token_entry(user_id, new_refresh_token, new_jti, datetime.now(timezone.utc) + timedelta(days=7), db)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }

def logout(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    revoke_refresh_token(jti, db)

    return {"message": "Logged out"}