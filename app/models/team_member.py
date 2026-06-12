from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship
from app.models.base import TimestampMixin
from app.core.database import Base

class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    role = Column(String(10), default="member", nullable=False) # owner, admin, member
    status = Column(String(10), default="invited", nullable=False) # invited, active, removed

    __table_args__ = (UniqueConstraint("user_id", "team_id", name="uq_user_team"),)

    # --- RELATIONSHIPS ---
    user = relationship("User", back_populates="team_memberships")
    team = relationship("Team", back_populates="members")
