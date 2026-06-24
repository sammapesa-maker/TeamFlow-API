from typing import Optional

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team_member import TeamMember
from app.schemas.team_member import TeamMemberQueryParams


# Helper Functions
def _apply_filters(stmt: Select, query: TeamMemberQueryParams) -> Select:
    if query.user_id is not None:
        stmt = stmt.where(TeamMember.user_id == query.user_id)

    if query.team_id is not None:
        stmt = stmt.where(TeamMember.team_id == query.team_id)

    if query.role is not None:
        stmt = stmt.where(TeamMember.role == query.role)

    if query.status is not None:
        stmt = stmt.where(TeamMember.status == query.status)

    return stmt


def _apply_sorting(stmt: Select, query: TeamMemberQueryParams) -> Select:
    sort_column_value = query.sort_by.value

    # Determine if the sorting direction is descending
    if sort_column_value[0] == "-":
        sort_column_name: str = sort_column_value[1:]
        stmt = stmt.order_by(desc(getattr(TeamMember, sort_column_name)))
    else:
        stmt = stmt.order_by(asc(getattr(TeamMember, sort_column_value)))

    return stmt


def _apply_pagination(stmt: Select, query: TeamMemberQueryParams) -> Select:
    return stmt.offset(query.offset).limit(query.limit)


async def _get_total_count(db: AsyncSession, query: TeamMemberQueryParams) -> int:
    count_stmt = select(func.count()).select_from(TeamMember)
    count_stmt = _apply_filters(count_stmt, query)

    result = await db.execute(count_stmt)
    return result.scalar_one()


async def create_team_member(
    db: AsyncSession,
    user_id: int,
    team_id: int,
    role: str = "member",
    status: str = "active",
) -> Optional[TeamMember]:
    member = TeamMember(
        user_id=user_id,
        team_id=team_id,
        role=role,
        status=status,
    )
    try:
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member
    except IntegrityError:
        await db.rollback()
        return None  # likely duplicate due to UniqueConstraint


async def get_team_member_by_id(db: AsyncSession, member_id: int):
    results = await db.execute(select(TeamMember).where(TeamMember.id == member_id))
    return results.scalar_one_or_none()


async def get_team_id_from_member_id(db: AsyncSession, member_id: int):
    result = await db.execute(
        select(TeamMember.team_id).where(TeamMember.id == member_id)
    )
    return result.scalar_one_or_none()


async def get_team_members(db: AsyncSession, query: TeamMemberQueryParams):
    stmt = select(TeamMember)
    stmt = _apply_filters(stmt, query)
    stmt = _apply_sorting(stmt, query)
    stmt = _apply_pagination(stmt, query)

    total = await _get_total_count(db, query)
    results = await db.execute(stmt)
    return total, results.scalars().all()


async def get_team_member(db: AsyncSession, user_id: int, team_id: int):
    member = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    )
    return member.scalar_one_or_none()


async def update_team_member(
    db: AsyncSession,
    member_id: int,
    role: Optional[str] = None,
    status: Optional[str] = None,
):
    member = await get_team_member_by_id(db, member_id)
    if not member:
        return None

    if role is not None:
        member.role = role
    if status is not None:
        member.status = status

    await db.commit()
    await db.refresh(member)
    return member


async def delete_team_member(db: AsyncSession, member_id: int) -> bool:
    member = await get_team_member_by_id(db, member_id)
    if not member:
        return False

    member.status = "removed"
    await db.commit()
    return True


async def remove_user_from_team(db: AsyncSession, user_id: int, team_id: int) -> bool:
    member = await get_team_member(db, user_id, team_id)
    if not member:
        return False

    member.status = "removed"
    await db.commit()
    return True
