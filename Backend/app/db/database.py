from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine
engine = create_async_engine(settings.database_url, echo=True)

# Create session factory
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session