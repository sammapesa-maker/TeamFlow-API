from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.team import Team
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
    return results


async def get_team_by_name(db: AsyncSession, name: str):
    results = await db.execute(select(Team).where(Team.name == name))
    return results


async def get_teams_by_owner(db: AsyncSession, owner_id: int):
    results = await db.execute(select(Team).where(Team.owner_id == owner_id))
    return results


async def list_teams(db: AsyncSession, skip: int = 0, limit: int = 100):
    results = await db.execute(select(Team).offset(skip).limit(limit))
    return results


async def update_team(
    db: AsyncSession,
    team_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    team = db.execute(select(Team).where(Team.id == team_id))
    if not team:
        return None

    if name is not None:
        team.name = name  # ty:ignore[unresolved-attribute]
    if description is not None:
        team.description = description  # ty:ignore[unresolved-attribute]

    await db.commit()
    await db.refresh(team)
    return team


async def delete_team(db: AsyncSession, team_id: int) -> bool:
    team = db.execute(select(Team).where(Team.id == team_id))
    if not team:
        return False

    await db.delete(team)
    await db.commit()
    return True
