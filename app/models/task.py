from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(10), default="todo", nullable=False)  # todo/progress/done
    priority = Column(String(10), default="medium", nullable=False)  # low/medium/high
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # --- RELATIONSHIPS ---
    team = relationship("Team", back_populates="tasks")
    creator = relationship(
        "User", back_populates="created_tasks", foreign_keys=[creator_id]
    )
    assignee = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id]
    )
