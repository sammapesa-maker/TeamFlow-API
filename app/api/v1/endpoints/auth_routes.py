from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas import auth_schemas
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])


@router.post(
    path="/register",
    response_model=auth_schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: auth_schemas.UserRegister, db: AsyncSession = Depends(get_db)
):
    user = await auth_service.register_user(db=db, user_data=user_data)
    return user


@router.post(
    path="/login-json",
    response_model=auth_schemas.TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_json(
    user_data: auth_schemas.UserLogin, db: AsyncSession = Depends(get_db)
):
    return await auth_service.login_user(user_data=user_data, db=db)


@router.post(
    path="/refresh",
    response_model=auth_schemas.TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def refresh(
    token: auth_schemas.RefreshTokenIn, db: AsyncSession = Depends(get_db)
):
    return await auth_service.refresh_token(token=token.token, db=db)


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: auth_schemas.RefreshTokenIn, db: AsyncSession = Depends(get_db)
):
    await auth_service.logout(token=token.token, db=db)


@router.post(
    path="/login",
    response_model=auth_schemas.TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    return await auth_service.login_form(form_data=form_data, db=db)


@router.patch(path="/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: auth_schemas.ChangePassword,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await auth_service.change_password(data=data, db=db, user_id=user.id)  # ty:ignore[invalid-argument-type]


@router.get(
    path="/me", response_model=auth_schemas.UserResponse, status_code=status.HTTP_200_OK
)
async def get_user(user: User = Depends(get_current_active_user)):
    return user


@router.patch(
    path="/me", response_model=auth_schemas.UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(
    data: auth_schemas.UserUpdate,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.update_profile(data=data, user=user, db=db)


@router.delete(path="/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    await auth_service.delete_user_service(user=user, db=db)
