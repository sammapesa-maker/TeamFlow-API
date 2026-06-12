from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.team_member import (
    create_team_member,
    get_team_member_by_id,
    get_team_member,
    list_team_members,
    list_user_teams,
    update_team_member,
)


# -----------------------
# CREATE
# -----------------------

def add_team_member_service(
    db: Session,
    user_id: int,
    team_id: int,
    role: str = "member",
):
    member = create_team_member(
        db,
        user_id=user_id,
        team_id=team_id,
        role=role,
        status="invited",
    )

    if not member:
        raise HTTPException(
            status_code=400,
            detail="User already in team or constraint violation",
        )

    return member


# -----------------------
# READ
# -----------------------

def get_team_member_service(db: Session, member_id: int):
    member = get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return member


def get_user_team_membership_service(db: Session, user_id: int, team_id: int):
    member = get_team_member(db, user_id, team_id)

    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")

    return member


def list_team_members_service(db: Session, team_id: int):
    return list_team_members(db, team_id)


def list_user_teams_service(db: Session, user_id: int):
    return list_user_teams(db, user_id)


# -----------------------
# UPDATE
# -----------------------

def update_team_member_service(
    db: Session,
    member_id: int,
    role: str | None = None,
    status: str | None = None,
):
    member = get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return update_team_member(
        db,
        member_id=member_id,
        role=role,
        status=status,
    )


# -----------------------
# DELETE / REMOVE
# -----------------------

def remove_team_member_service(db: Session, member_id: int):
    member = get_team_member_by_id(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return update_team_member(
        db,
        member_id=member_id,
        status="removed",
    )


def remove_user_from_team_service(db: Session, user_id: int, team_id: int):
    member = get_team_member(db, user_id, team_id)

    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")

    return update_team_member(
        db,
        member_id=member.id, # type: ignore
        status="removed",
    )