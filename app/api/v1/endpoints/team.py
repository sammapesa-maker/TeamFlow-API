from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.services.team import (
    create_team_service,
    get_team_service,
    list_teams_service,
    update_team_service,
    delete_team_service,
    get_teams_by_owner_service,
)

from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamRead,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


# OPTIONAL: replace later with real auth
def get_current_user():
    pass


# -----------------------
# CREATE TEAM
# -----------------------
@router.post("/", response_model=TeamRead)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return create_team_service(
        db=db,
        name=payload.name,
        owner_id=user.id,  # enforce ownership from auth
        description=payload.description,
    )


# -----------------------
# GET TEAM BY ID
# -----------------------
@router.get("/{team_id}", response_model=TeamRead)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
):
    return get_team_service(db, team_id)


# -----------------------
# LIST TEAMS
# -----------------------
@router.get("/", response_model=list[TeamRead])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return list_teams_service(db, skip, limit)


# -----------------------
# GET TEAMS BY OWNER
# -----------------------
@router.get("/owner/{owner_id}", response_model=list[TeamRead])
def teams_by_owner(
    owner_id: int,
    db: Session = Depends(get_db),
):
    return get_teams_by_owner_service(db, owner_id)


# -----------------------
# UPDATE TEAM
# -----------------------
@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
):
    return update_team_service(
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
):
    return delete_team_service(db, team_id)