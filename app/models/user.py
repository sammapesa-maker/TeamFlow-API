from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import TimestampMixin
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(40), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)

    # --- RELATIONSHIPS ---

    # Teams owned by user
    owned_teams = relationship("Team", back_populates="owner", cascade="all, delete")

    # Memberships
    team_memberships = relationship(
        "TeamMember", back_populates="user", cascade="all, delete"
    )

    # Tasks created by user
    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )

    # Tasks assigned to user
    assigned_tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to_id"
    )
