from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from app.models.team_member import TeamMember


def create_team_member(
    db: Session,
    user_id: int,
    team_id: int,
    role: str = "member",
    status: str = "invited",
) -> Optional[TeamMember]:
    member = TeamMember(
        user_id=user_id,
        team_id=team_id,
        role=role,
        status=status,
    )
    try:
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    except IntegrityError:
        db.rollback()
        return None  # likely duplicate due to UniqueConstraint


def get_team_member_by_id(db: Session, member_id: int) -> Optional[TeamMember]:
    return db.query(TeamMember).filter(TeamMember.id == member_id).first()


def get_team_member(
    db: Session, user_id: int, team_id: int
) -> Optional[TeamMember]:
    return (
        db.query(TeamMember)
        .filter(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
        .first()
    )


def list_team_members(db: Session, team_id: int) -> List[TeamMember]:
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()


def list_user_teams(db: Session, user_id: int) -> List[TeamMember]:
    return db.query(TeamMember).filter(TeamMember.user_id == user_id).all()


def update_team_member(
    db: Session,
    member_id: int,
    role: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[TeamMember]:
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        return None

    if role is not None:
        member.role = role # type:ignore
    if status is not None:
        member.status = status # type: ignore

    db.commit()
    db.refresh(member)
    return member


def delete_team_member(db: Session, member_id: int) -> bool:
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        return False

    member.status = "removed" # type: ignore
    db.commit()
    return True


def remove_user_from_team(db: Session, user_id: int, team_id: int) -> bool:
    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
        .first()
    )
    if not member:
        return False

    member.status = "removed" # type: ignore
    db.commit()
    return True