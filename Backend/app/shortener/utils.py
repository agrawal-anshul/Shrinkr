import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models

SHORTCODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits

async def generate_unique_short_code(db: AsyncSession) -> str:
    while True:
        code = ''.join(random.choices(ALPHABET, k=SHORTCODE_LENGTH))
        stmt = select(models.URL).where(models.URL.short_code == code)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            return code