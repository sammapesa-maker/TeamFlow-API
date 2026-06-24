from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.team_member import (
    create_team_member,
    get_team_member,
    get_team_member_by_id,
    get_team_members,
    update_team_member,
)
from app.schemas.team_member import PaginatedTeamMemberResponse, TeamMemberQueryParams


async def add_team_member_service(
    db: AsyncSession,
    user_id: int,
    team_id: int,
    role: str = "member",
):
    member = await create_team_member(
        db,
        user_id=user_id,
        team_id=team_id,
        role=role,
        status="invited",
    )

    if not member:
        raise HTTPException(
            status_code=400,
            detail="User already in team or constraint violation",
        )

    return member


# -----------------------
# READ
# -----------------------


async def get_team_member_service(db: AsyncSession, member_id: int):
    member = await get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return member


async def get_user_team_membership_service(
    db: AsyncSession, user_id: int, team_id: int
):
    member = await get_team_member(db, user_id, team_id)

    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")

    return member


async def get_team_members_service(
    db: AsyncSession, query: TeamMemberQueryParams
) -> PaginatedTeamMemberResponse:
    total, results = await get_team_members(db, query)

    return PaginatedTeamMemberResponse(
        total=total, limit=query.limit, offset=query.offset, items=results
    )


# -----------------------
# UPDATE
# -----------------------


async def update_team_member_service(
    db: AsyncSession,
    member_id: int,
    role: str | None = None,
    status: str | None = None,
):
    member = await get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return await update_team_member(
        db,
        member_id=member_id,
        role=role,
        status=status,
    )


# -----------------------
# DELETE / REMOVE
# -----------------------


async def remove_team_member_service(db: AsyncSession, member_id: int):
    member = await get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    await update_team_member(
        db,
        member_id=member_id,
        status="removed",
    )


async def remove_user_from_team_service(db: AsyncSession, user_id: int, team_id: int):
    member = await get_team_member(db, user_id, team_id)

    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")

    return await update_team_member(
        db,
        member_id=member.id,
        status="removed",
    )
