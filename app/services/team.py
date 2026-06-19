from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.user import User
from app.models.team import Team
from app.repositories.team import (
    get_team_by_id,
    get_team_by_name,
    create_team,
    update_team,
    delete_team,
    get_user_teams
)
from app.repositories.team_member import create_team_member


async def create_team_service(
    db: AsyncSession,
    name: str,
    user: User,
    description: str | None = None,
):
    # check duplicate name (optional but recommended)
    existing = await get_team_by_name(db, name)
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")

    team = await create_team(db=db, name=name, owner_id=user.id, description=description)  # type: ignore

    # add initial member as owner
    await create_team_member(db=db, user_id=user.id, team_id=team.id, role="owner", status="active")  # ty:ignore[invalid-argument-type]

    return team


async def get_team_service(db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


async def list_teams_service(
    user: User, db: AsyncSession, skip: int = 0, limit: int = 100
):
    return await get_user_teams(db=db, user_id=user.id)  # ty:ignore[invalid-argument-type]



async def update_team_service(
    db: AsyncSession,
    team_id: int,
    name: str | None = None,
    description: str | None = None,
):
    team: Team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # optional: prevent duplicate names
    if name and name != team.name:
        existing = await get_team_by_name(db, name)
        if existing:
            raise HTTPException(status_code=400, detail="Team name already exists")

    updated = await update_team(db, team_id, name=name, description=description)

    return updated



async def delete_team_service(db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return await delete_team(db, team_id)
