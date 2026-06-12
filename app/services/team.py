from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.repositories.team import (
    get_team_by_id,
    get_team_by_name,
    create_team,
    update_team,
    delete_team,
    get_teams_by_owner,
    list_teams,
)
from app.repositories.team_member import create_team_member

def is_owner(user_id: int, resource_id: int):
    return user_id == resource_id


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

    team = create_team(db, name, owner_id, description) # type: ignore
    
    # add initial member as owner
    create_team_member(db, owner_id, team.id, "owner", "active")  # ty:ignore[invalid-argument-type]
    
    return team

# -----------------------
# READ
# -----------------------

def get_team_service(user: User, db: Session, team_id: int):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

    return team


def list_teams_service(user: User, db: Session, skip: int = 0, limit: int = 100):
    if user.is_superuser:
        return list_teams(db)
    
    return get_teams_by_owner(db, user.id)  # ty:ignore[invalid-argument-type]


def get_teams_by_owner_service(db: Session, owner_id: int):
    return get_teams_by_owner(db, owner_id)


# -----------------------
# UPDATE
# -----------------------

def update_team_service(
    user: User,
    db: Session,
    team_id: int,
    name: str | None = None,
    description: str | None = None,
):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

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

def delete_team_service(user: User, db: Session, team_id: int):
    team = get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if not is_owner(user.id, team.owner_id):  # ty:ignore[invalid-argument-type]
        raise HTTPException(status_code=401, detail="Unauthorized")

    return delete_team(db, team_id)