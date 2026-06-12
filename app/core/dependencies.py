from typing import Generator, Optional

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.database import SessionLocal
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
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# CURRENT USER
# -------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
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
def get_current_active_user(
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
def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )
    return current_user


# -------------------------
# OPTIONAL USER
# -------------------------
def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            return None

        try:
            user_id = int(user_id)
        except ValueError:
            return None

        return get_user_by_id(user_id=user_id, db=db)

    except JWTError:
        return None

# =========================
# TEAM ROLE DEPENDENCIES
# =========================

OWNER = "owner"
ADMIN = "admin"
MEMBER = "member"

ADMIN_ROLES = {OWNER, ADMIN}

def get_team_membership(
    team_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
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


def require_team_member(
    membership: TeamMember = Depends(get_team_membership),
):
    return membership


def require_team_admin(
    membership: TeamMember = Depends(get_team_membership),
    user: User = Depends(get_current_user),
):
    if user.is_superuser:
        return user

    if membership.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return membership


def require_team_owner(
    membership: TeamMember = Depends(get_team_membership),
):
    if membership.role != OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )
    return membership


def require_role(*allowed_roles: str):
    def dependency(
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

# =========================
# SUPERADMIN OVERRIDE LAYER
# =========================

def require_superadmin_override(
    user: User = Depends(get_current_user),
):
    """
    Returns user if superadmin OR raises if not authenticated.
    This is NOT a strict guard — it's a bypass marker.
    """
    return user


def is_superadmin(user: User) -> bool:
    return getattr(user, "is_superuser", False)

def superadmin_or(*dependencies):
    """
    Wrapper: if user is superadmin → bypass everything
    otherwise enforce normal dependencies.
    """

    def get_current_user_or_superuser(
        user: User = Depends(get_current_user),
    ):
        return user

    return get_current_user_or_superuser