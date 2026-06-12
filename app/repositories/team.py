from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.team import Team


def create_team(db: Session, name: str, owner_id: int, description: str = None) -> Team: # type : ignore
    team = Team(name=name, owner_id=owner_id, description=description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team_by_id(db: Session, team_id: int) -> Optional[Team]:
    return db.query(Team).filter(Team.id == team_id).first()


def get_team_by_name(db: Session, name: str) -> Optional[Team]:
    return db.query(Team).filter(Team.name == name).first()


def get_teams_by_owner(db: Session, owner_id: int) -> List[Team]:
    return db.query(Team).filter(Team.owner_id == owner_id).all()


def list_teams(db: Session, skip: int = 0, limit: int = 100) -> List[Team]:
    return db.query(Team).offset(skip).limit(limit).all()


def update_team(
    db: Session,
    team_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Team]:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None

    if name is not None:
        team.name = name  # ty:ignore[invalid-assignment]
    if description is not None:
        team.description = description  # ty:ignore[invalid-assignment]

    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team_id: int) -> bool:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return False

    db.delete(team)
    db.commit()
    return True