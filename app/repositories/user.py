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
    return results


async def get_user_by_username(username: str, db: AsyncSession):
    results = await db.execute(select(User).where(User.username == username))
    return results


async def get_user_by_id(user_id: int, db: AsyncSession):
    results = await db.execute(select(User).where(User.id == user_id))
    return results


async def update_user(
    user: User,
    db: AsyncSession,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> User:
    """
    Partial update of user fields
    """

    if username is not None:
        user.username = username  # type: ignore

    if email is not None:
        user.email = email  # type: ignore

    if is_active is not None:
        user.is_active = is_active  # type: ignore

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user: User, db: AsyncSession) -> None:
    """
    Deletes a user instance (soft delete)
    """
    user.is_active = False  # type : ignore
    await db.commit()


async def get_all_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
):
    results = await db.execute(select(User).offset(skip).limit(limit))
    return results.scalars().all()


async def update_user_password(
    user: User, hashed_password: str, db: AsyncSession
) -> User:
    user.hashed_password = hashed_password  # type: ignore
    await db.commit()
    await db.refresh(user)
    return user
