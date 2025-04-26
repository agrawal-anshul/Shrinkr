from sqlalchemy import text
from app.db.database import engine

async def run_migrations():
    async with engine.begin() as conn:
        # Add tags column to urls table
        await conn.execute(text("""
            ALTER TABLE urls 
            ADD COLUMN IF NOT EXISTS tags JSONB;
        """))

        # Add new columns to click_logs table
        await conn.execute(text("""
            ALTER TABLE click_logs 
            ADD COLUMN IF NOT EXISTS country VARCHAR(2),
            ADD COLUMN IF NOT EXISTS city VARCHAR(100),
            ADD COLUMN IF NOT EXISTS device_type VARCHAR(50),
            ADD COLUMN IF NOT EXISTS browser VARCHAR(50),
            ADD COLUMN IF NOT EXISTS os VARCHAR(50),
            ADD COLUMN IF NOT EXISTS is_mobile BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS is_bot BOOLEAN DEFAULT FALSE;
        """)) 