from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.dependencies import (
    get_current_active_user,
    get_db,
    require_team_admin,
    require_team_admin_from_task,
    require_team_member,
    require_team_member_from_task,
)
from app.models.user import User
from app.schemas.task import (
    PaginatedTaskResponse,
    TaskCreate,
    TaskQueryParams,
    TaskRead,
    TaskSortField,
    TaskUpdate,
    TaskStatusEnum,
    TaskPriorityEnum
)
from app.services.task import (
    create_task_service,
    delete_task_service,
    get_task_service,
    list_tasks_service,
    update_task_service,
)

router = APIRouter(prefix="", tags=["Tasks"])

def get_task_query_params(
    title_contains: Annotated[str | None, Query()] = None,
    status: Annotated[TaskStatusEnum | None, Query()] = None,
    priority: Annotated[TaskPriorityEnum | None, Query()] = None,
    creator_id: Annotated[int | None, Query(ge=1)] = None,
    assigned_to_id: Annotated[int | None, Query()] = None,
    sort_by: Annotated[TaskSortField, Query()] = TaskSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
) -> TaskQueryParams:
    return TaskQueryParams(
        title_contains=title_contains,
        status=status,
        priority=priority,
        creator_id=creator_id,
        assigned_to_id=assigned_to_id,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )


@router.post("/teams/{team_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    _: None = Depends(require_team_admin),
):
    return await create_task_service(
        db=db,
        title=payload.title,
        team_id=team_id,
        creator_id=user.id,  # ty:ignore[invalid-argument-type]
        description=payload.description,
        priority=payload.priority,
    )


@router.get("/tasks/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member_from_task),
):
    return await get_task_service(db, task_id)


@router.get("/teams/{team_id}/tasks", response_model=PaginatedTaskResponse, status_code=status.HTTP_200_OK)
async def list_tasks(
    team_id: int,
    query: TaskQueryParams = Depends(get_task_query_params),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_member)
):
    query.team_id = team_id
    return await list_tasks_service(db, query)


@router.patch("/tasks/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member_from_task),
):
    return await update_task_service(
        db=db,
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assigned_to_id=payload.assigned_to_id,
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin_from_task),
):
    await delete_task_service(db, task_id)
