# init_db.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import engine, get_async_session
from app.db.models import Base, User
from app.core.logger import logger

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # optional for testing
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created.")

    # Initialize with get_async_session
    async for session in get_async_session():
        try:
            # Insert test user
            test_user = User(email="test@example.com", password_hash="fakehash123")
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            logger.info(f"�� Test user created: ID={test_user.id}, Email={test_user.email}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            await session.rollback()
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(init_db())