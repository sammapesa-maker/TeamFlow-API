from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.team import Team
from app.models.team_member import TeamMember
from sqlalchemy import select


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
        select(Team)
        .join(TeamMember)
        .where(TeamMember.user_id == user_id)
    )
    return results.scalars().all()


async def list_teams(db: AsyncSession, skip: int = 0, limit: int = 100):
    results = await db.execute(select(Team).offset(skip).limit(limit))
    return results.scalar_one_or_none()


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


async def delete_team(db: AsyncSession, team_id: int) -> bool:
    team = await get_team_by_id(db, team_id)
    if not team:
        return False

    await db.delete(team)
    await db.commit()
    return True
