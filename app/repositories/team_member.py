from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.exc import IntegrityError
from app.models.team_member import TeamMember
from sqlalchemy import select


async def create_team_member(
    db: AsyncSession,
    user_id: int,
    team_id: int,
    role: str = "member",
    status: str = "invited",
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


# Checking if a user is part of a team
async def get_team_member(db: AsyncSession, user_id: int, team_id: int):
    results = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    )
    return results.scalar_one_or_none()


async def list_team_members(db: AsyncSession, team_id: int):
    results = await db.execute(select(TeamMember).where(TeamMember.team_id == team_id))
    return results.scalars().all()


async def list_all_memberships(db):
    results = await db.execute(select(TeamMember))
    return results.scalars().all()


async def update_team_member(
    db: AsyncSession,
    member_id: int,
    role: Optional[str] = None,
    status: Optional[str] = None,
):
    member = await get_team_member_by_id(db,member_id)
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
    member = await get_team_member_by_id(db,member_id)
    if not member:
        return False

    member.status = "removed"
    await db.commit()
    return True


async def remove_user_from_team(db: AsyncSession, user_id: int, team_id: int) -> bool:
    member = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    )
    member = member.scalar_one_or_none()
    if not member:
        return False

    member.status = "removed"  # ty:ignore[invalid-assignment]
    await db.commit()
    return True
