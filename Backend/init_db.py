import asyncio
from app.db.models import Base
from app.db.database import engine

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Optional: start fresh
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized.")

if __name__ == "__main__":
    asyncio.run(init())