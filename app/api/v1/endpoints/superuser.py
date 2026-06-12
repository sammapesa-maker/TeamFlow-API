from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_superuser

from app.services.superuser import (
    list_users,
    promote_to_superuser,
    demote_superuser,
    activate_user,
    deactivate_user,
    delete_user,
)

from app.services.team import (
    list_teams_service,
    delete_team_service,
)

from app.services.team_member import (
    list_team_members_service,
    remove_user_from_team_service,
)

from app.services.task import (
    list_tasks_service,
    delete_task_service,
)

from app.schemas.auth_schemas import UserResponse
from app.schemas.team import TeamRead
from app.schemas.team_member import TeamMemberRead
from app.schemas.task import TaskRead

router = APIRouter(prefix="/admin", tags=["Super Admin"])


# =========================
# USERS
# =========================
@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    return list_users(db)


@router.patch("/users/{user_id}/promote")
def promote(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return promote_to_superuser(db, user_id)


@router.patch("/users/{user_id}/demote")
def demote(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return demote_superuser(db, user_id)


@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    delete_user(db, user_id)
    return {"status": "deleted"}


# =========================
# TEAMS (GLOBAL CONTROL)
# =========================
@router.get("/teams", response_model=list[TeamRead])
def get_teams(db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return list_teams_service(db)


@router.delete("/teams/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return delete_team_service(db, team_id)


# =========================
# TEAM MEMBERS (GLOBAL CONTROL)
# =========================
@router.get("/team-members", response_model=list[TeamMemberRead])
def get_members(
    team_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return list_team_members_service(db, team_id)


@router.delete("/team-members/{team_id}/user/{user_id}")
def remove_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return remove_user_from_team_service(db, user_id, team_id)


# =========================
# TASKS (GLOBAL CONTROL)
# =========================
@router.get("/tasks", response_model=list[TaskRead])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return list_tasks_service(db, skip, limit)


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return delete_task_service(db, task_id)