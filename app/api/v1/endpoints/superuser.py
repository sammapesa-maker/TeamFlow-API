from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_superuser
from app.schemas.auth_schemas import UserResponse
from app.schemas.team import TeamRead
from app.schemas.team_member import TeamMemberRead
from app.schemas.task import TaskRead
from app.services.auth_service import get_all_users_service, get_user_profile
from app.services.team import get_all_teams_service, get_team_service
from app.services.team_member import get_all_memberships, get_team_member_by_id
from app.services.task import list_all_tasks_service, get_task_by_id

router = APIRouter(prefix="/admin", tags=["SuperUser"])

@router.get(path="/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_all_users_service(db)

@router.get(path="/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_user_profile(db,user_id)


@router.get(path="/teams", response_model=list[TeamRead], status_code=status.HTTP_200_OK)
async def get_all_teams(
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_all_teams_service(db)

@router.get(path="/teams/{team_id}", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_team_service(db,team_id)


@router.get(path="/members", response_model=list[TeamMemberRead], status_code=status.HTTP_200_OK)
async def get_all_members(
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_all_memberships(db)

@router.get(path="/members/{member_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_team_member_by_id(db,member_id)


@router.get(path="/tasks", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def get_all_tasks(
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await list_all_tasks_service(db)

@router.get(path="/tasks/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_task_by_id(db,task_id)