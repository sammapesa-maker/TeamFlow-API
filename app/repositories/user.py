from typing import Optional

from sqlalchemy import select, Select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth_schemas import UserQueryParams
from app.models.user import User


# Helper Functions
def _apply_filters(stmt: Select, query: UserQueryParams) -> Select:
    if query.username_contains is not None:
        stmt = stmt.where(User.username.ilike(f"%{query.username_contains}%"))

    if query.is_active is not None:
        stmt = stmt.where(User.is_active == query.is_active)

    if query.is_superuser is not None:
        stmt = stmt.where(User.is_superuser == query.is_superuser)

    return stmt


def _apply_sorting(stmt: Select, query: UserQueryParams) -> Select:
    sort_column_value = query.sort_by.value

    # Determine if the sorting direction is descending
    if sort_column_value[0] == "-":
        sort_column_name: str = sort_column_value[1:]
        stmt = stmt.order_by(desc(getattr(User, sort_column_name)))
    else:
        stmt = stmt.order_by(asc(getattr(User, sort_column_value)))

    return stmt


def _apply_pagination(stmt: Select, query: UserQueryParams) -> Select:
    return stmt.offset(query.offset).limit(query.limit)


async def _get_total_count(db: AsyncSession, query: UserQueryParams) -> int:
    count_stmt = select(func.count()).select_from(User)
    count_stmt = _apply_filters(count_stmt, query)

    result = await db.execute(count_stmt)
    return result.scalar_one()


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
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
) -> User:
    """
    Partial update of user fields
    """

    user = await get_user_by_id(user_id, db)
    if username is not None:
        user.username = username

    if email is not None:
        user.email = email

    if is_active is not None:
        user.is_active = is_active

    if is_superuser is not None:
        user.is_superuser = is_superuser

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(user_id: int, db: AsyncSession):
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


async def delete_user(user: User, db: AsyncSession):
    await db.delete(user)
    await db.commit()


async def get_users(db: AsyncSession, query: UserQueryParams):
    stmt = select(User)
    stmt = _apply_filters(stmt, query)
    stmt = _apply_sorting(stmt, query)
    stmt = _apply_pagination(stmt, query)

    total = await _get_total_count(db, query)
    results = await db.execute(stmt)
    return total, results.scalars().all()


async def update_user_password(
    user: User, hashed_password: str, db: AsyncSession
) -> User:
    user.hashed_password = hashed_password  # type: ignore
    await db.commit()
    await db.refresh(user)
    return user
