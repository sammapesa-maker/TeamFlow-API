from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # ty:ignore[no-matching-overload]

Base = declarative_base()
