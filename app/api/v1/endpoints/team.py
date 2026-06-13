from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
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


@router.post("/", response_model=TeamRead)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_team_service(
        db=db,
        name=payload.name,
        owner_id=user.id,  # ty:ignore[invalid-argument-type]
        description=payload.description,
    )


@router.get("/{team_id}", response_model=TeamRead)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_team_service(user, db, team_id)


@router.get("/", response_model=list[TeamRead])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # add filtering, sorting, searching and pagination
    return list_teams_service(user, db, skip, limit)


# -----------------------
# UPDATE TEAM
# -----------------------
@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return update_team_service(
        user=user,
        db=db,
        team_id=team_id,
        name=payload.name,
        description=payload.description,
    )


# -----------------------
# DELETE TEAM
# -----------------------
@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    return delete_team_service(user, db, team_id)