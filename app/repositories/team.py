from typing import Optional

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.team_member import TeamMember
from app.schemas.team import TeamQueryParams


# Helper Functions
def _apply_filters(stmt: Select, query: TeamQueryParams) -> Select:
    if query.name_contains is not None:
        stmt = stmt.where(Team.name.ilike(f"%{query.name_contains}%"))

    if query.owner_id is not None:
        stmt = stmt.where(Team.owner_id == query.owner_id)

    return stmt


def _apply_sorting(stmt: Select, query: TeamQueryParams) -> Select:
    sort_column_value = query.sort_by.value

    # Determine if the sorting direction is descending
    if sort_column_value[0] == "-":
        sort_column_name: str = sort_column_value[1:]
        stmt = stmt.order_by(desc(getattr(Team, sort_column_name)))
    else:
        stmt = stmt.order_by(asc(getattr(Team, sort_column_value)))

    return stmt


def _apply_pagination(stmt: Select, query: TeamQueryParams) -> Select:
    return stmt.offset(query.offset).limit(query.limit)


async def _get_total_count(db: AsyncSession, query: TeamQueryParams) -> int:
    count_stmt = select(func.count()).select_from(Team)
    count_stmt = _apply_filters(count_stmt, query)

    result = await db.execute(count_stmt)
    return result.scalar_one()


async def create_team(
    db: AsyncSession, name: str, owner_id: int, description: str | None = None
):
    team = Team(name=name, owner_id=owner_id, description=description)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def get_team_by_id(db: AsyncSession, team_id: int):
    results = await db.execute(select(Team).where(Team.id == team_id))
    return results.scalar_one_or_none()


async def get_team_by_name(db: AsyncSession, name: str):
    results = await db.execute(select(Team).where(Team.name == name))
    return results.scalar_one_or_none()


async def get_user_teams(db: AsyncSession, user_id: int):
    results = await db.execute(
        select(Team).join(TeamMember).where(TeamMember.user_id == user_id)
    )
    return results.scalars().all()


async def get_teams(db: AsyncSession, query: TeamQueryParams):
    stmt = select(Team)
    stmt = _apply_filters(stmt, query)
    stmt = _apply_sorting(stmt, query)
    stmt = _apply_pagination(stmt, query)

    total = await _get_total_count(db, query)
    results = await db.execute(stmt)
    return total, results.scalars().all()


async def update_team(
    db: AsyncSession,
    team_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    team = await get_team_by_id(db, team_id)
    if not team:
        return None

    if name is not None:
        team.name = name
    if description is not None:
        team.description = description

    await db.commit()
    await db.refresh(team)
    return team


async def delete_team(db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)
    if not team:
        return False

    await db.delete(team)
    await db.commit()
