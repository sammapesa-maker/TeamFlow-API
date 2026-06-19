from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_team_admin,
    require_team_member,
    require_team_owner
)
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamRead,
    TeamUpdate,
)
from app.services.team import (
    create_team_service,
    delete_team_service,
    get_team_service,
    list_teams_service,
    update_team_service,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
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
    _ = Depends(require_team_member),
):
    return await get_team_service(db=db, team_id=team_id)


@router.get("/", response_model=list[TeamRead], status_code=status.HTTP_200_OK)
async def list_teams(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # add filtering, sorting, searching and pagination
    return await list_teams_service(user, db)


# -----------------------
# UPDATE TEAM
# -----------------------
@router.patch("/{team_id}", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_team_admin),
):
    return await update_team_service(
        db=db,
        team_id=team_id,
        name=payload.name,
        description=payload.description,
    )


# -----------------------
# DELETE TEAM
# -----------------------
@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_team_owner),
):
    await delete_team_service(db, team_id)
