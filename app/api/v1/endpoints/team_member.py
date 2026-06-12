from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.services.team_member import (
    add_team_member_service,
    get_team_member_service,
    get_user_team_membership_service,
    list_team_members_service,
    list_user_teams_service,
    update_team_member_service,
    remove_team_member_service,
    remove_user_from_team_service,
)

from app.schemas.team_member import (
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberRead,
)

from app.core.dependencies import (
    require_team_admin,
    require_team_member,
)

router = APIRouter(prefix="/team-members", tags=["Team Members"])


# -----------------------
# ADD MEMBER (INVITE)
# -----------------------
@router.post("/", response_model=TeamMemberRead)
def add_member(
    payload: TeamMemberCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),  # only admin/owner can invite
):
    return add_team_member_service(
        db=db,
        user_id=payload.user_id,
        team_id=payload.team_id,
        role=payload.role,
    )


# -----------------------
# GET MEMBER BY ID
# -----------------------
@router.get("/{member_id}", response_model=TeamMemberRead)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return get_team_member_service(db, member_id)


# -----------------------
# GET USER TEAM MEMBERSHIP
# -----------------------
@router.get("/user/{user_id}/team/{team_id}", response_model=TeamMemberRead)
def get_membership(
    user_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return get_user_team_membership_service(db, user_id, team_id)


# -----------------------
# LIST TEAM MEMBERS
# -----------------------
@router.get("/team/{team_id}", response_model=list[TeamMemberRead])
def list_members(
    team_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return list_team_members_service(db, team_id)


# -----------------------
# LIST USER TEAMS
# -----------------------
@router.get("/user/{user_id}/teams", response_model=list[TeamMemberRead])
def list_user_teams(
    user_id: int,
    db: Session = Depends(get_db),
):
    return list_user_teams_service(db, user_id)


# -----------------------
# UPDATE MEMBER (ROLE / STATUS)
# -----------------------
@router.patch("/{member_id}", response_model=TeamMemberRead)
def update_member(
    member_id: int,
    payload: TeamMemberUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return update_team_member_service(
        db=db,
        member_id=member_id,
        role=payload.role,
        status=payload.status,
    )


# -----------------------
# REMOVE MEMBER (SOFT REMOVE)
# -----------------------
@router.delete("/{member_id}", response_model=TeamMemberRead)
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return remove_team_member_service(db, member_id)


# -----------------------
# REMOVE USER FROM TEAM
# -----------------------
@router.delete("/team/{team_id}/user/{user_id}", response_model=TeamMemberRead)
def remove_user(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return remove_user_from_team_service(db, user_id, team_id)