from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.team import Team
from app.repositories.team import get_team_by_id
from app.repositories.task import (
    create_task,
    get_task_by_id,
    list_tasks,
    update_task,
    delete_task,
)


async def create_task_service(
    db: AsyncSession,
    title: str,
    team_id: int,
    creator_id: int,
    description: str | None = None,
    priority: str = "medium",
):
    team: Team = await get_team_by_id(db, team_id)
    if team:
        return await create_task(
            db,
            title=title,
            team_id=team_id,
            creator_id=creator_id,
            description=description,  # type: ignore
            priority=priority,
        )
    else:
        raise HTTPException(status_code=404, detail="Team not found")


async def get_task_service(db: AsyncSession, task_id: int):
    task = await get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


async def list_tasks_service(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await list_tasks(db, skip, limit)


async def update_task_service(
    db: AsyncSession,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assigned_to_id: int | None = None,
):
    task = await get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return await update_task(
        db,
        task_id=task_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to_id,
    )


async def delete_task_service(db: AsyncSession, task_id: int):
    task = await get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await delete_task(db, task_id)
