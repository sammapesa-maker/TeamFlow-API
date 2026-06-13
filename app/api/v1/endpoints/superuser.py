from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_superuser, get_db
from app.models.user import User
from app.schemas.auth_schemas import UserResponse
from app.schemas.task import TaskRead
from app.schemas.team import TeamRead
from app.schemas.team_member import TeamMemberRead
from app.services.superuser import (
    delete_user,
    list_users,
)
from app.services.task import (
    delete_task_service,
    list_tasks_service,
)
from app.services.team import (
    delete_team_service,
    list_teams_service,
)
from app.services.team_member import list_team_members_service

router = APIRouter(prefix="/admin", tags=["Super Admin"])


# =========================
# USERS
# =========================
@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    # add sorting. filtering, pagination and searching
    return list_users(db)

# router.post(/users/)
# router.get(/users/{id})
# router.patch(/users/{id})

@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    delete_user(db, user_id)
    return {"status": "deleted"}


# =========================
# TEAMS (GLOBAL CONTROL)
# =========================
@router.get("/teams", response_model=list[TeamRead])
def get_teams(db: Session = Depends(get_db), user: User =Depends(get_current_superuser)):
    # add sorting. filtering, pagination and searching
    return list_teams_service(user, db)


@router.delete("/teams/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), user: User =Depends(get_current_superuser)):
    return delete_team_service(user, db, team_id)

# router.post(/teams/)
# router.get(/teams/{id})
# router.patch(/teams/{id})

# =========================
# TEAM MEMBERS (GLOBAL CONTROL)
# =========================
@router.get("/team-members", response_model=list[TeamMemberRead])
def get_members(
    team_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    # add sorting. filtering, pagination and searching
    return list_team_members_service(db, team_id)

# router.post(/team-members/)
# router.get(/team-members/{id}/)
# router.patch(/team-members/{id})
# router.delete(/team-members/{id})


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
    # add sorting. filtering, pagination and searching
    return list_tasks_service(db, skip, limit)


# router.post(/tasks/)
# router.get(/tasks/{id}/)
# router.patch(/tasks/{id})
# router.delete(/tasks/{id})

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_superuser),
):
    return delete_task_service(db, task_id)