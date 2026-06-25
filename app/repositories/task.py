from typing import Optional

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskQueryParams


# Helper Functions
def _apply_filters(stmt: Select, query: TaskQueryParams) -> Select:
    if query.title_contains is not None:
        stmt = stmt.where(Task.name.ilike(f"%{query.title_contains}%"))

    if query.creator_id is not None:
        stmt = stmt.where(Task.owner_id == query.creator_id)

    if query.assigned_to_id is not None:
        stmt = stmt.where(Task.owner_id == query.assigned_to_id)

    if query.team_id is not None:
        stmt = stmt.where(Task.owner_id == query.team_id)

    if query.priority is not None:
        stmt = stmt.where(Task.priority == query.priority)

    if query.status is not None:
        stmt = stmt.where(Task.status == query.status)

    return stmt


def _apply_sorting(stmt: Select, query: TaskQueryParams) -> Select:
    sort_column_value = query.sort_by.value

    # Determine if the sorting direction is descending
    if sort_column_value[0] == "-":
        sort_column_name: str = sort_column_value[1:]
        stmt = stmt.order_by(desc(getattr(Task, sort_column_name)))
    else:
        stmt = stmt.order_by(asc(getattr(Task, sort_column_value)))

    return stmt


def _apply_pagination(stmt: Select, query: TaskQueryParams) -> Select:
    return stmt.offset(query.offset).limit(query.limit)


async def _get_total_count(db: AsyncSession, query: TaskQueryParams) -> int:
    count_stmt = select(func.count()).select_from(Task)
    count_stmt = _apply_filters(count_stmt, query)

    result = await db.execute(count_stmt)
    return result.scalar_one()


async def create_task(
    db: AsyncSession,
    title: str,
    team_id: int,
    creator_id: int,
    description: str | None = None,
    status: str = "todo",
    priority: str = "medium",
    assigned_to_id: int | None = None,
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
    return results.scalar_one_or_none()


async def list_tasks(db: AsyncSession, query: TaskQueryParams):
    stmt = select(Task)
    stmt = _apply_filters(stmt, query)
    stmt = _apply_sorting(stmt, query)
    stmt = _apply_pagination(stmt, query)

    total = await _get_total_count(db, query)
    results = await db.execute(stmt)
    return total, results.scalars().all()


async def get_team_id_from_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task.team_id).where((Task.id == task_id)))
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
):
    task = await get_task_by_id(db, task_id)
    if not task:
        return None

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    if priority is not None:
        task.priority = priority
    if assigned_to_id is not None:
        task.assigned_to_id = assigned_to_id

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()
