from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.services.task import (
    create_task_service,
    delete_task_service,
    get_task_service,
    list_tasks_service,
    update_task_service,
)

router = APIRouter(prefix="", tags=["Tasks"])


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


@router.get("/teams/{team_id}/tasks", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def list_tasks(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_member)
):
    # change inputs
    # add filtering, searching, sorting and pagination
    return await list_tasks_service(db, team_id)


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
