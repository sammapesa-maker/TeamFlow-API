from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.task import (
    create_task,
    get_task_by_id,
    list_tasks,
    get_tasks_by_team,
    get_tasks_by_creator,
    get_tasks_by_assignee,
    update_task,
    delete_task,
    get_tasks_by_status,
    get_tasks_by_priority,
    get_tasks_by_team_and_status,
    assign_task,
    change_task_status,
)


# -----------------------
# CREATE
# -----------------------

def create_task_service(
    db: Session,
    title: str,
    team_id: int,
    creator_id: int,
    description: str | None = None,
    priority: str = "medium",
):
    return create_task(
        db,
        title=title,
        team_id=team_id,
        creator_id=creator_id,
        description=description, #type: ignore
        priority=priority,
    )


# -----------------------
# READ
# -----------------------

def get_task_service(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def list_tasks_service(db: Session, skip: int = 0, limit: int = 100):
    return list_tasks(db, skip, limit)


def get_tasks_by_team_service(db: Session, team_id: int):
    return get_tasks_by_team(db, team_id)


def get_tasks_by_creator_service(db: Session, creator_id: int):
    return get_tasks_by_creator(db, creator_id)


def get_tasks_by_assignee_service(db: Session, user_id: int):
    return get_tasks_by_assignee(db, user_id)


# -----------------------
# UPDATE
# -----------------------

def update_task_service(
    db: Session,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assigned_to_id: int | None = None,
):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return update_task(
        db,
        task_id=task_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to_id,
    )


# -----------------------
# DELETE
# -----------------------

def delete_task_service(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return delete_task(db, task_id)


# -----------------------
# FILTER SERVICES
# -----------------------

def get_tasks_by_status_service(db: Session, status: str):
    return get_tasks_by_status(db, status)


def get_tasks_by_priority_service(db: Session, priority: str):
    return get_tasks_by_priority(db, priority)


def get_tasks_by_team_and_status_service(db: Session, team_id: int, status: str):
    return get_tasks_by_team_and_status(db, team_id, status)


# -----------------------
# ACTIONS
# -----------------------

def assign_task_service(db: Session, task_id: int, user_id: int | None):
    task = assign_task(db, task_id, user_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def change_task_status_service(db: Session, task_id: int, status: str):
    task = change_task_status(db, task_id, status)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task