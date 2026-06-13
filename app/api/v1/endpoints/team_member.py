from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    require_team_admin,
    require_team_member,
)
from app.schemas.team_member import (
    TeamMemberCreate,
    TeamMemberRead,
    TeamMemberReadDetailed,
    TeamMemberUpdate
)
from app.services.team_member import (
    add_team_member_service,
    get_team_member_service,
    remove_team_member_service,
    update_team_member_service,
)

router = APIRouter(prefix="/team-members", tags=["Team Members"])


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


@router.get("/", response_model=list[TeamMemberRead])
def get_members(
    member_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    # to add search, filter, sort and paginate
    return get_team_member_service(db, member_id)


@router.get("/{member_id}", response_model=TeamMemberReadDetailed)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return get_team_member_service(db, member_id)


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


@router.delete("/{member_id}", response_model=TeamMemberRead)
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return remove_team_member_service(db, member_id)
