from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_db,
    require_team_admin,
    require_team_member,
    require_team_admin_from_member,
    require_team_member_from_member
)
from app.schemas.team_member import (
    TeamMemberCreate,
    TeamMemberRead,
    TeamMemberUpdate,
)
from app.services.team_member import (
    add_team_member_service,
    get_team_member_service,
    remove_team_member_service,
    update_team_member_service,
    list_team_members_service
)

router = APIRouter(prefix="", tags=["Team Members"])


@router.post("/teams/{team_id}/members", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    payload: TeamMemberCreate,
    team_id:int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),  # only admin/owner can invite
):
    return await add_team_member_service(
        db=db,
        user_id=payload.user_id,
        team_id=team_id,
        role=payload.role,
    )


@router.get("/teams/{team_id}/members", response_model=list[TeamMemberRead], status_code=status.HTTP_200_OK)
async def get_members(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    # to add search, filter, sort and paginate
    return await list_team_members_service(db, team_id)


@router.get("/team-member/{member_id}", response_model=TeamMemberRead, status_code=status.HTTP_200_OK)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member_from_member),
):
    return await get_team_member_service(db, member_id)


@router.patch("/team-member/{member_id}", response_model=TeamMemberRead, status_code=status.HTTP_200_OK)
async def update_member(
    member_id: int,
    payload: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin_from_member),
):
    return await update_team_member_service(
        db=db,
        member_id=member_id,
        role=payload.role,
        status=payload.status,
    )


@router.delete("/team-member/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin_from_member),
):
    await remove_team_member_service(db, member_id)
