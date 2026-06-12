# models/team.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import TimestampMixin
from app.core.database import Base


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- RELATIONSHIPS ---

    owner = relationship("User", back_populates="owned_teams")
    members = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="team", cascade="all, delete-orphan")
