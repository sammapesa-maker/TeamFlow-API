from sqlalchemy import Column, String, DateTime, Boolean, Text
from app.core.database import Base
from app.models.base import TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
