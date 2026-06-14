from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_superuser, get_db
from app.services import superuser
from app.schemas.auth_schemas import UserRegister, UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["Super Admin"])


# =========================
# USERS
# =========================
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserRegister,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    return await superuser.create_user(user=user, db=db)


@router.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    # add sorting. filtering, pagination and searching
    return await superuser.list_users(db)


@router.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    return await superuser.get_user(db=db, user_id=user_id)


@router.patch("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_data: UserUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return await superuser.update_user(db=db, user_id=user_id, user_data=user_data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_superuser)
):
    await superuser.delete_user(db=db, user_id=user_id)
    return {"status": "deleted"}


@router.patch("/users/{user_id}/promote-to-superuser", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def promote_to_superuser(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_superuser)
):
    return await superuser.promote_to_superuser(db=db, user_id=user_id)


@router.patch("/users/{user_id}/demote-superuser", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def demote_superuser(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_superuser)
):
    return await superuser.demote_superuser(db=db, user_id=user_id)


@router.patch("/users/{user_id}/activate-user", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def activate_user(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_superuser)
):
    return await superuser.activate_user(db=db, user_id=user_id)


@router.patch("/users/{user_id}/deactivate-user", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_superuser)
):
    return await superuser.deactivate_user(db=db, user_id=user_id)


# Implement Team, Memberships and Tasks management globally
