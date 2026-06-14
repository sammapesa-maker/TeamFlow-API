from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.user import User
from app.repositories.team import (
    get_team_by_id,
    get_team_by_name,
    create_team,
    update_team,
    delete_team,
    get_teams_by_owner,
    list_teams,
)
from app.repositories.team_member import create_team_member


def is_owner(user_id: int, resource_id: int):
    return user_id == resource_id


# -----------------------
# CREATE
# -----------------------


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

    team = await create_team(db, name, user.id, description)  # type: ignore

    # add initial member as owner
    await create_team_member(db, user.id, team.id, "owner", "active")  # ty:ignore[invalid-argument-type]

    return team


# -----------------------
# READ
# -----------------------


async def get_team_service(user: User, db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

    return team


async def list_teams_service(
    user: User, db: AsyncSession, skip: int = 0, limit: int = 100
):
    if user.is_superuser:
        return await list_teams(db)

    return await get_teams_by_owner(db, user.id)  # ty:ignore[invalid-argument-type]


async def get_teams_by_owner_service(db: AsyncSession, owner_id: int):
    return await get_teams_by_owner(db, owner_id)


# -----------------------
# UPDATE
# -----------------------


async def update_team_service(
    user: User,
    db: AsyncSession,
    team_id: int,
    name: str | None = None,
    description: str | None = None,
):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

    # optional: prevent duplicate names
    if name and name != team.name:
        existing = await get_team_by_name(db, name)
        if existing:
            raise HTTPException(status_code=400, detail="Team name already exists")

    updated = await update_team(db, team_id, name=name, description=description)

    return updated


# -----------------------
# DELETE
# -----------------------


async def delete_team_service(user: User, db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await delete_team(db, team_id)
