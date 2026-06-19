from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.security import oauth2_scheme
from app.models.team_member import TeamMember
from app.models.user import User
from app.repositories.team_member import get_team_id_from_member_id, get_team_member
from app.repositories.user import get_user_by_id
from app.repositories.task import get_team_id_from_task

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# -------------------------
# DB DEPENDENCY
# -------------------------
async def get_db():
    async with AsyncSessionLocal() as session:  # ty:ignore[invalid-context-manager]
        yield session


# -------------------------
# CURRENT USER
# -------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await get_user_by_id(user_id=user_id, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# -------------------------
# ACTIVE USER
# -------------------------
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user



# ---------------------------
# TEAM ROLE CONSTANTS
# ---------------------------

OWNER = "owner"
ADMIN = "admin"
MEMBER = "member"

ADMIN_ROLES = {OWNER, ADMIN}


# ---------------------------
# CORE RESOLVERS
# ---------------------------

async def get_team_membership(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> TeamMember | None:

    membership = await get_team_member(
        db=db,
        user_id=user.id,  # ty:ignore[invalid-argument-type]
        team_id=team_id,
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a team member",
        )

    return membership


async def get_team_membership_from_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> TeamMember | None:
    
    # get team_id from member_id
    team_id = await get_team_id_from_member_id(db, member_id)

    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )

    # reuse main resolver
    return await get_team_membership(team_id, db, user)


async def get_team_membership_from_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> TeamMember | None:
    
    # get team_id from member_id
    team_id = await get_team_id_from_task(db, task_id)

    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )

    # reuse main resolver
    return await get_team_membership(team_id, db, user)


# ---------------------------
# ROLE CHECKS (TEAM_ID)
# ---------------------------

async def require_team_member(
    membership: TeamMember = Depends(get_team_membership),
):
    return membership


async def require_team_admin(
    membership: TeamMember = Depends(get_team_membership),
    user: User = Depends(get_current_active_user),
):
    if membership.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return membership


async def require_team_owner(
    membership: TeamMember = Depends(get_team_membership),
    user: User = Depends(get_current_active_user),
):
    if membership.role != OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )

    return membership

# ---------------------------
# ROLE CHECKS (MEMBER_ID)
# ---------------------------

async def require_team_member_from_member(
    membership: TeamMember = Depends(get_team_membership_from_member),
):
    return membership


async def require_team_admin_from_member(
    membership: TeamMember = Depends(get_team_membership_from_member),
    user: User = Depends(get_current_active_user),
):
    if membership.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return membership

# ---------------------------
# ROLE CHECKS (TASK_ID)
# ---------------------------

async def require_team_member_from_task(
    membership: TeamMember = Depends(get_team_membership_from_task),
):
    return membership


async def require_team_admin_from_task(
    membership: TeamMember = Depends(get_team_membership_from_task),
    user: User = Depends(get_current_active_user),
):
    if membership.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return membership