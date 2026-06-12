from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.services.task import (
    create_task_service,
    get_task_service,
    list_tasks_service,
    get_tasks_by_team_service,
    get_tasks_by_creator_service,
    get_tasks_by_assignee_service,
    update_task_service,
    delete_task_service,
    get_tasks_by_status_service,
    get_tasks_by_priority_service,
    get_tasks_by_team_and_status_service,
    assign_task_service,
    change_task_status_service,
)

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
)

from app.core.dependencies import (
    require_team_member,
    require_team_admin,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# -----------------------
# CREATE TASK
# -----------------------
@router.post("/", response_model=TaskRead)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    # creator_id should come from auth in real system
    return create_task_service(
        db=db,
        title=payload.title,
        team_id=payload.team_id,
        creator_id=payload.team_id,  # replace with current_user.id
        description=payload.description,
        priority=payload.priority,
    )


# -----------------------
# GET TASK BY ID
# -----------------------
@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return get_task_service(db, task_id)


# -----------------------
# LIST TASKS
# -----------------------
@router.get("/", response_model=list[TaskRead])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return list_tasks_service(db, skip, limit)


# -----------------------
# FILTERS
# -----------------------
@router.get("/team/{team_id}", response_model=list[TaskRead])
def tasks_by_team(
    team_id: int,
    db: Session = Depends(get_db),
):
    return get_tasks_by_team_service(db, team_id)


@router.get("/creator/{creator_id}", response_model=list[TaskRead])
def tasks_by_creator(
    creator_id: int,
    db: Session = Depends(get_db),
):
    return get_tasks_by_creator_service(db, creator_id)


@router.get("/assignee/{user_id}", response_model=list[TaskRead])
def tasks_by_assignee(
    user_id: int,
    db: Session = Depends(get_db),
):
    return get_tasks_by_assignee_service(db, user_id)


@router.get("/status/{status}", response_model=list[TaskRead])
def tasks_by_status(
    status: str,
    db: Session = Depends(get_db),
):
    return get_tasks_by_status_service(db, status)


@router.get("/priority/{priority}", response_model=list[TaskRead])
def tasks_by_priority(
    priority: str,
    db: Session = Depends(get_db),
):
    return get_tasks_by_priority_service(db, priority)


@router.get("/team/{team_id}/status/{status}", response_model=list[TaskRead])
def tasks_by_team_and_status(
    team_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    return get_tasks_by_team_and_status_service(db, team_id, status)


# -----------------------
# UPDATE TASK
# -----------------------
@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return update_task_service(
        db=db,
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assigned_to_id=payload.assigned_to_id,
    )


# -----------------------
# DELETE TASK
# -----------------------
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return delete_task_service(db, task_id)


# -----------------------
# ACTION: ASSIGN TASK
# -----------------------
@router.patch("/{task_id}/assign", response_model=TaskRead)
def assign_task(
    task_id: int,
    user_id: int | None,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    return assign_task_service(db, task_id, user_id)


# -----------------------
# ACTION: CHANGE STATUS
# -----------------------
@router.patch("/{task_id}/status", response_model=TaskRead)
def change_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return change_task_status_service(db, task_id, status)