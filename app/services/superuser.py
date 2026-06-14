from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import user as user_crud
from app.schemas.auth_schemas import UserRegister, UserUpdate
from app.services.auth_service import register_user



async def promote_to_superuser(db: AsyncSession, user_id: int) -> User:
    user = await user_crud.promote_to_superuser(db, user_id)
    return user


async def demote_superuser(db: AsyncSession, user_id: int) -> User:
    user = await user_crud.demote_superuser(db, user_id)
    return user


async def deactivate_user(db: AsyncSession, user_id: int) -> User:
    user = await user_crud.deactivate_user(user_id, db)
    return user


async def activate_user(db: AsyncSession, user_id: int) -> User:
    user = await user_crud.activate_user(db, user_id)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    await user_crud.delete_user(user_id, db)


async def list_users(db: AsyncSession) -> list[User]:
    return await user_crud.get_all_users(db)


async def create_user(user: UserRegister, db: AsyncSession):
    return await register_user(user_data=user, db=db)


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate):
    return await user_crud.update_user(
        user_id, 
        db, 
        username=user_data.username, 
        email=user_data.email
)
