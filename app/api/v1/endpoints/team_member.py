from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_db,
    require_team_admin,
    require_team_member,
)
from app.schemas.team_member import (
    TeamMemberCreate,
    TeamMemberRead,
    TeamMemberReadDetailed,
    TeamMemberUpdate,
)
from app.services.team_member import (
    add_team_member_service,
    get_team_member_service,
    remove_team_member_service,
    update_team_member_service,
)

router = APIRouter(prefix="/team-members", tags=["Team Members"])


@router.post("/", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    payload: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),  # only admin/owner can invite
):
    return await add_team_member_service(
        db=db,
        user_id=payload.user_id,
        team_id=payload.team_id,
        role=payload.role,
    )


@router.get("/", response_model=list[TeamMemberRead], status_code=status.HTTP_200_OK)
async def get_members(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    # to add search, filter, sort and paginate
    return await get_team_member_service(db, member_id)


@router.get("/{member_id}", response_model=TeamMemberReadDetailed, status_code=status.HTTP_200_OK)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return await get_team_member_service(db, member_id)


@router.patch("/{member_id}", response_model=TeamMemberRead, status_code=status.HTTP_200_OK)
async def update_member(
    member_id: int,
    payload: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return await update_team_member_service(
        db=db,
        member_id=member_id,
        role=payload.role,
        status=payload.status,
    )


@router.delete("/{member_id}", response_model=TeamMemberRead, status_code=status.HTTP_200_OK)
async def remove_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return await remove_team_member_service(db, member_id)
