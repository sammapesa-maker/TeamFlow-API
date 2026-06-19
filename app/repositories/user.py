from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from typing import Optional
from sqlalchemy import select


async def create_user(
    email: str, username: str, hashed_password: str, db: AsyncSession
) -> User:
    user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(email: str, db: AsyncSession):
    results = await db.execute(select(User).where(User.email == email))
    return results.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession):
    results = await db.execute(select(User).where(User.username == username))
    return results.scalar_one_or_none()


async def get_user_by_id(user_id: int, db: AsyncSession):
    results = await db.execute(select(User).where(User.id == user_id))
    return results.scalar_one_or_none()


async def update_user(
    user_id: int,
    db: AsyncSession,
    username: Optional[str] = None,
    email: Optional[str] = None,
) -> User:
    """
    Partial update of user fields
    """

    user = await get_user_by_id(user_id, db)
    if username is not None:
        user.username = username

    if email is not None:
        user.email = email

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(user_id:int, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    user.is_active = False
    await db.commit()
    return user


async def activate_user(db: AsyncSession, user_id: int) -> User:
    user = await get_user_by_id(user_id, db)

    if not user.is_active:
        user.is_active = True
        await db.commit()
        await db.refresh(user)

    return user


async def delete_user(user_id: int, db: AsyncSession) -> None:
    user = await get_user_by_id(user_id, db)
    await db.delete(user)
    await db.commit()


async def get_all_users(
    db: AsyncSession
):
    results = await db.execute(select(User))
    return results.scalars().all()


async def update_user_password(
    user: User, hashed_password: str, db: AsyncSession
) -> User:
    user.hashed_password = hashed_password  # type: ignore
    await db.commit()
    await db.refresh(user)
    return user
