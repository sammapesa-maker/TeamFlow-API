from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_db,
    require_team_admin,
    require_team_admin_from_member,
    require_team_member,
    require_team_member_from_member,
)
from app.schemas.team_member import (
    PaginatedTeamMemberResponse,
    TeamMemberCreate,
    TeamMemberQueryParams,
    TeamMemberRead,
    TeamMemberRoleEnum,
    TeamMemberSortField,
    TeamMemberStatusEnum,
    TeamMemberUpdate,
)
from app.services.team_member import (
    add_team_member_service,
    delete_team_member_service,
    get_team_member_service,
    get_team_members_service,
    update_team_member_service,
)

router = APIRouter(prefix="", tags=["Team Members"])


def get_member_query_params(
    user_id: Annotated[int | None, Query(ge=1)] = None,
    role: Annotated[TeamMemberRoleEnum | None, Query()] = None,
    status: Annotated[TeamMemberStatusEnum | None, Query()] = None,
    sort_by: Annotated[TeamMemberSortField, Query()] = TeamMemberSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return TeamMemberQueryParams(
        user_id=user_id,
        role=role,
        status=status,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/teams/{team_id}/members",
    response_model=TeamMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    payload: TeamMemberCreate,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return await add_team_member_service(
        db=db,
        user_id=payload.user_id,
        team_id=team_id,
        role=payload.role,
    )


@router.get(
    "/teams/{team_id}/members",
    response_model=PaginatedTeamMemberResponse,
    status_code=status.HTTP_200_OK,
)
async def get_members(
    team_id: int,
    query: TeamMemberQueryParams = Depends(get_member_query_params),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    query.team_id = team_id
    return await get_team_members_service(db, query)


@router.get(
    "/team-member/{member_id}",
    response_model=TeamMemberRead,
    status_code=status.HTTP_200_OK,
)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member_from_member),
):
    return await get_team_member_service(db, member_id)


@router.patch(
    "/team-member/{member_id}",
    response_model=TeamMemberRead,
    status_code=status.HTTP_200_OK,
)
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
async def delete_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin_from_member),
):
    await delete_team_member_service(db, member_id)
