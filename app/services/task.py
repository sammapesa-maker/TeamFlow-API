from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.task import (
    create_task,
    get_task_by_id,
    list_tasks,
    update_task,
    delete_task
)


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


def get_task_service(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def list_tasks_service(db: Session, skip: int = 0, limit: int = 100):
    return list_tasks(db, skip, limit)


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


def delete_task_service(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return delete_task(db, task_id)
