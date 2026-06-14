from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.task import Task
from sqlalchemy import select

async def create_task(
    db: AsyncSession,
    title: str,
    team_id: int,
    creator_id: int,
    description: str = None,  # type: ignore
    status: str = "todo",
    priority: str = "medium",
    assigned_to_id: int = None,  # type: ignore
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
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_id(db: AsyncSession, task_id: int):
    results = await db.execute(select(Task).where(Task.id == task_id))
    return results


async def list_tasks(db: AsyncSession, skip: int = 0, limit: int = 100):
    results = await db.execute(select(Task).offset(skip).limit(limit))
    return results.scalars().all()


async def update_task(
    db: AsyncSession,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
):
    task = db.execute(select(Task).where(Task.id == task_id))
    if not task:
        return None

    if title is not None:
        task.title = title  # type:ignore
    if description is not None:
        task.description = description  # type:ignore
    if status is not None:
        task.status = status  # type:ignore
    if priority is not None:
        task.priority = priority  # type:ignore
    if assigned_to_id is not None:
        task.assigned_to_id = assigned_to_id  # type:ignore

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = db.execute(select(Task).where(Task.id == task_id))
    if not task:
        return False

    await db.delete(task)
    await db.commit()
    return True
