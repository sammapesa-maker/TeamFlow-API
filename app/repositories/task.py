from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.task import Task


def create_task(
    db: Session,
    title: str,
    team_id: int,
    creator_id: int,
    description: str = None, # type: ignore
    status: str = "todo",
    priority: str = "medium",
    assigned_to_id: int = None, # type: ignore
) -> Task:
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        team_id=team_id,
        creator_id=creator_id,
        assigned_to_id=assigned_to_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).offset(skip).limit(limit).all()


def get_tasks_by_team(db: Session, team_id: int) -> List[Task]:
    return db.query(Task).filter(Task.team_id == team_id).all()


def get_tasks_by_creator(db: Session, creator_id: int) -> List[Task]:
    return db.query(Task).filter(Task.creator_id == creator_id).all()


def get_tasks_by_assignee(db: Session, assigned_to_id: int) -> List[Task]:
    return (
        db.query(Task)
        .filter(Task.assigned_to_id == assigned_to_id)
        .all()
    )


def update_task(
    db: Session,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    if title is not None:
        task.title = title # type:ignore
    if description is not None:
        task.description = description # type:ignore
    if status is not None:
        task.status = status # type:ignore
    if priority is not None:
        task.priority = priority # type:ignore
    if assigned_to_id is not None:
        task.assigned_to_id = assigned_to_id # type:ignore

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True


# --- FILTERS ---

def get_tasks_by_status(db: Session, status: str) -> List[Task]:
    return db.query(Task).filter(Task.status == status).all()


def get_tasks_by_priority(db: Session, priority: str) -> List[Task]:
    return db.query(Task).filter(Task.priority == priority).all()


def get_tasks_by_team_and_status(
    db: Session, team_id: int, status: str
) -> List[Task]:
    return (
        db.query(Task)
        .filter(
            Task.team_id == team_id,
            Task.status == status,
        )
        .all()
    )


# --- ACTIONS ---

def assign_task(
    db: Session, task_id: int, user_id: Optional[int]
) -> Optional[Task]:
    """
    Assign or unassign a task.
    Pass user_id=None to unassign.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    task.assigned_to_id = user_id # type : ignore
    db.commit()
    db.refresh(task)
    return task


def change_task_status(
    db: Session, task_id: int, status: str
) -> Optional[Task]:
    """
    Change task status (todo, in_progress, done).
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    task.status = status # type: ignore
    db.commit()
    db.refresh(task)
    return task