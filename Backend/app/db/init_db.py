# init_db.py

import asyncio
from app.db.models import Base, User
from app.db.database import engine, async_session
from app.core.logger import logger

async def init():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # optional for testing
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created.")

    # Insert test user
    async with async_session() as session:
        test_user = User(email="test@example.com", password_hash="fakehash123")
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        logger.info(f"🙋 Test user created: ID={test_user.id}, Email={test_user.email}")

if __name__ == "__main__":
    asyncio.run(init())