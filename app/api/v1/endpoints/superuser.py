from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_superuser
from app.schemas.auth_schemas import (
    PaginatedUserResponse,
    UserQueryParams,
    UserResponse,
    UserSortField,
)
from app.schemas.task import TaskRead
from app.schemas.team import (
    PaginatedTeamResponse,
    TeamQueryParams,
    TeamRead,
    TeamSortField,
)
from app.schemas.team_member import (
    PaginatedTeamMemberResponse,
    TeamMemberQueryParams,
    TeamMemberRoleEnum,
    TeamMemberStatusEnum,
    TeamMemberSortField,
    PaginatedTeamMemberResponse
)
from app.services.auth_service import get_user_profile, get_users_service
from app.services.task import get_task_by_id, list_all_tasks_service
from app.services.team import get_team_service, get_teams_service
from app.services.team_member import get_team_member_by_id, get_team_members_service

router = APIRouter(prefix="/admin", tags=["SuperUser"])

def get_user_query_params(
    username_contains: Annotated[str | None, Query(description="Partial username match")] = None,
    is_active: Annotated[bool | None, Query(description="State of the user")] = None,
    is_superuser: Annotated[bool | None, Query(description="Superuser privilege")] = None,
    sort_by: Annotated[UserSortField, Query()] = UserSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
) -> UserQueryParams:
    return UserQueryParams(
        username_contains=username_contains,
        is_active=is_active,
        is_superuser=is_superuser,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )


def get_team_query_params(
    name_contains: Annotated[str | None, Query(description="Partial name match")] = None,
    owner_id: Annotated[int | None, Query(description="Team's Owner id")] = None,
    sort_by: Annotated[TeamSortField, Query()] = TeamSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
) -> TeamQueryParams:
    return TeamQueryParams(
        name_contains=name_contains,
        owner_id=owner_id,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )


def get_member_query_params(
    user_id: Annotated[int | None, Query(ge=1)] = None,
    team_id: Annotated[int | None, Query(ge=1)] = None,
    role: Annotated[TeamMemberRoleEnum | None, Query()] = None,
    status: Annotated[TeamMemberStatusEnum | None, Query()] = None,
    sort_by: Annotated[TeamMemberSortField, Query()] = TeamMemberSortField.id,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
):
    return TeamMemberQueryParams(
        user_id=user_id,
        team_id=team_id,
        role=role,
        status=status,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )



@router.get(path="/users", response_model=PaginatedUserResponse, status_code=status.HTTP_200_OK)
async def get_all_users(
    query: Annotated[UserQueryParams, Depends(get_user_query_params)],
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_users_service(db, query)

@router.get(path="/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_user_profile(db,user_id)


@router.get(path="/teams", response_model=PaginatedTeamResponse, status_code=status.HTTP_200_OK)
async def get_all_teams(
    query: TeamQueryParams = Depends(get_team_query_params),
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_teams_service(db, query)

@router.get(path="/teams/{team_id}", response_model=TeamRead, status_code=status.HTTP_200_OK)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_team_service(db,team_id)


@router.get(path="/members", response_model=PaginatedTeamMemberResponse, status_code=status.HTTP_200_OK)
async def get_all_members(
    query: TeamMemberQueryParams = Depends(get_member_query_params),
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_team_members_service(db, query)

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