from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.core.security import oauth2_scheme
from app.models.user import User
from app.repositories.user import get_user_by_id

from app.models.team_member import TeamMember


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

    user = get_user_by_id(user_id=user_id, db=db)

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


# -------------------------
# SUPERUSER
# -------------------------
async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )
    return current_user


# =========================
# TEAM ROLE DEPENDENCIES
# =========================

OWNER = "owner"
ADMIN = "admin"
MEMBER = "member"

ADMIN_ROLES = {OWNER, ADMIN}


async def get_team_membership(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> Optional[TeamMember]:

    # SUPERADMIN BYPASS
    if user.is_superuser:
        return None  # or fake membership if needed

    membership = (
        db.query(TeamMember)
        .filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a team member",
        )

    return membership


async def require_team_member(
    membership: TeamMember = Depends(get_team_membership),
):
    return membership


async def require_team_admin(
    membership: TeamMember = Depends(get_team_membership),
    user: User = Depends(get_current_active_user),
):
    if user.is_superuser:
        return user

    if membership.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return membership


async def require_team_owner(
    membership: TeamMember = Depends(get_team_membership),
):
    if membership.role != OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )
    return membership


async def require_role(*allowed_roles: str):
    async def dependency(
        membership: TeamMember = Depends(get_team_membership),
    ):
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return membership

    return dependency


# Prebuilt shortcuts
require_admin_or_owner = require_role(OWNER, ADMIN)
require_owner_only = require_role(OWNER)
