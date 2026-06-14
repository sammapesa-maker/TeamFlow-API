from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from datetime import datetime, timedelta, timezone
from app.repositories.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user,
    update_user_password,
)
from app.core.config import get_settings, Settings
from jose import JWTError, jwt
from app.core.security import verify_token
from app.repositories.token import (
    get_refresh_token_by_jti,
    revoke_refresh_token,
    create_refresh_token_entry,
)
from app.schemas import auth_schemas
from app.models.user import User

settings: Settings = get_settings()
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM


async def register_user(user_data: UserRegister, db: AsyncSession):
    # Check if user already exists
    if await get_user_by_email(email=user_data.email, db=db) or await get_user_by_username(
        user_data.username, db
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    try:
        user = await create_user(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password.get_secret_value()),
            db=db,
        )
        return user

    except Exception as e:  # Any unhandled exceptions during user creation
        print(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration",
        )


async def login_user(user_data: UserLogin, db: AsyncSession):

    # check if identifier is email or username
    if "@" in user_data.identifier:
        user = await get_user_by_email(email=user_data.identifier, db=db)
    else:
        user = await get_user_by_username(username=user_data.identifier, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(
        plain_password=user_data.password.get_secret_value(),
        hashed_password=user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = await create_access_token(user_id=user.id)
    refresh_token, jti = await create_refresh_token(user_id=user.id)

    await create_refresh_token_entry(
        user_id=user.id,
        token=refresh_token,
        jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        db=db
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


async def refresh_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token=str(token), key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        print(f"Error : {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    user_id = payload.get("sub")

    db_token = await get_refresh_token_by_jti(jti, db)

    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Token revoked")

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")

    if not verify_token(token=token, hashed=db_token.token_hash):
        raise HTTPException(status_code=401, detail="Token mismatch")

    # ROTATION: revoke old token
    await revoke_refresh_token(jti, db)

    # Issue new tokens
    access_token = await create_access_token(user_id)
    new_refresh_token, new_jti = await create_refresh_token(user_id)

    await create_refresh_token_entry(
        user_id=user_id,
        token=new_refresh_token,
        jti=new_jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        db=db,
    )

    return {"access_token": access_token, "refresh_token": new_refresh_token}


async def logout(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    await revoke_refresh_token(jti, db)

    return {"message": "Logged out"}


async def login_form(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    username = form_data.username
    password = form_data.password
    user_data = UserLogin(
        identifier=username, password=SecretStr(secret_value=password)
    )
    return await login_user(user_data=user_data, db=db)


async def get_user_profile(db: AsyncSession, user_id: int):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def update_profile(data: auth_schemas.UserUpdate, user: User, db: AsyncSession):
    username: str | None = data.username
    email: str | None = data.email

    # email uniqueness check
    if email and email != user.email:
        existing = await get_user_by_email(email, db)
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    return update_user(
        user,
        db,
        username=username,
        email=email,
    )


async def change_password(
    data: auth_schemas.ChangePassword, db: AsyncSession, user_id: int
):
    old_password = data.current_password.get_secret_value()
    new_password = data.new_password.get_secret_value()

    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    hashed = hash_password(new_password)

    user = await update_user_password(user, hashed, db)

    if user:
        return {"message": "Password updated successfully", "user_id": user.id}
