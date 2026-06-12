from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.team import (
    get_team_by_id,
    get_team_by_name,
    create_team,
    update_team,
    delete_team,
    get_teams_by_owner,
    list_teams,
)


# -----------------------
# CREATE
# -----------------------

def create_team_service(
    db: Session,
    name: str,
    owner_id: int,
    description: str | None = None,
):
    # check duplicate name (optional but recommended)
    existing = get_team_by_name(db, name)
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")

    return create_team(db, name, owner_id, description) # type: ignore


# -----------------------
# READ
# -----------------------

def get_team_service(db: Session, team_id: int):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


def list_teams_service(db: Session, skip: int = 0, limit: int = 100):
    return list_teams(db, skip, limit)


def get_teams_by_owner_service(db: Session, owner_id: int):
    return get_teams_by_owner(db, owner_id)


# -----------------------
# UPDATE
# -----------------------

def update_team_service(
    db: Session,
    team_id: int,
    name: str | None = None,
    description: str | None = None,
):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # optional: prevent duplicate names
    if name and name != team.name:
        existing = get_team_by_name(db, name)
        if existing:
            raise HTTPException(status_code=400, detail="Team name already exists")

    updated = update_team(db, team_id, name=name, description=description)

    return updated


# -----------------------
# DELETE
# -----------------------

def delete_team_service(db: Session, team_id: int):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return delete_team(db, team_id)