from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.user import User
from app.repositories.team import (
    create_team,
    delete_team,
    get_team_by_id,
    get_team_by_name,
    get_teams,
    get_user_teams,
    update_team,
)
from app.repositories.team_member import create_team_member
from app.services.team_member import change_ownership
from app.schemas.team import PaginatedTeamResponse, TeamQueryParams


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

    team = await create_team(
        db=db,
        name=name,
        owner_id=user.id,  # ty:ignore[invalid-argument-type]
        description=description,
    )

    # add initial member as owner
    await create_team_member(
        db=db,
        user_id=user.id,  # ty:ignore[invalid-argument-type]
        team_id=team.id,
        role="owner",
        status="active",
    )

    return team


async def get_team_service(db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


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


async def transfer_ownership_service(db: AsyncSession, team_id: int, member_id: int):
    # update team_membership
    member = await change_ownership(db, member_id)

    # update teams owner_id
    return await update_team(db, team_id, owner_id=member.user_id)


async def delete_team_service(db: AsyncSession, team_id: int):
    team = await get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    await delete_team(db, team_id)


async def get_teams_service(
    db: AsyncSession, query: TeamQueryParams
) -> PaginatedTeamResponse:
    total, results = await get_teams(db, query)

    return PaginatedTeamResponse(
        total=total, limit=query.limit, offset=query.offset, items=results
    )


async def list_teams_service(user: User, db: AsyncSession):
    return await get_user_teams(db, user.id)  # ty:ignore[invalid-argument-type]
