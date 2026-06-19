from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repositories.team_member import (
    create_team_member,
    get_team_member_by_id,
    get_team_member,
    list_team_members,
    list_user_teams,
    update_team_member,
)


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


async def list_team_members_service(db: AsyncSession, team_id: int):
    return await list_team_members(db, team_id)


async def list_user_teams_service(db: AsyncSession, user_id: int):
    results = await list_user_teams(db, user_id)
    results = list(results)
    return results


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
