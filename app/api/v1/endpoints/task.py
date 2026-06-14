from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

from app.services.task import (
    create_task_service,
    get_task_service,
    list_tasks_service,
    update_task_service,
    delete_task_service,
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
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    # creator_id should come from auth in real system
    return await create_task_service(
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
@router.get("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
):
    return await get_task_service(db, task_id)


@router.get("/", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_team_member)
):
    # add filtering, searching, sorting and pagination
    return await list_tasks_service(db, skip, limit)


@router.patch("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_member),
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


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_team_admin),
):
    await delete_task_service(db, task_id)
