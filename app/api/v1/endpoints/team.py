from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_active_user,
    get_db,
    require_team_admin,
    require_team_member,
    require_team_owner,
)
from app.models.user import User
from app.schemas.team import (
    PaginatedTeamResponse,
    TeamCreate,
    TeamQueryParams,
    TeamRead,
    TeamSortField,
    TeamUpdate,
)
from app.services.team import (
    create_team_service,
    delete_team_service,
    get_team_service,
    get_teams_service,
    update_team_service,
    transfer_ownership_service,
)

router = APIRouter(prefix="/my-teams", tags=["Teams"])


def get_team_query_params(
    name_contains: Annotated[
        str | None, Query(description="Partial name match")
    ] = None,
    sort_by: Annotated[TeamSortField, Query()] = TeamSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TeamQueryParams:
    return TeamQueryParams(
        name_contains=name_contains, sort_by=sort_by, limit=limit, offset=offset
    )


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await create_team_service(
        db=db,
        name=payload.name,
        user=user,
        description=payload.description,
    )


@router.get("/{team_id}", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_member),
):
    return await get_team_service(db=db, team_id=team_id)


@router.get("/", response_model=PaginatedTeamResponse, status_code=status.HTTP_200_OK)
async def list_teams(
    query: TeamQueryParams = Depends(get_team_query_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    query.owner_id = user.id  # ty:ignore[invalid-assignment]
    return await get_teams_service(db, query)


# -----------------------
# UPDATE TEAM
# -----------------------
@router.patch("/{team_id}", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_admin),
):
    return await update_team_service(
        db=db,
        team_id=team_id,
        name=payload.name,
        description=payload.description,
    )


@router.patch("/{team_id}/transfer-ownership", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def transfer_ownership(team_id: int, member_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_team_owner)):
    return await transfer_ownership_service(db, team_id, member_id)


# -----------------------
# DELETE TEAM
# -----------------------
@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_owner),
):
    await delete_team_service(db, team_id)
