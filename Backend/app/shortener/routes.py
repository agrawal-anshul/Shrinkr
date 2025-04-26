from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models, schemas
from app.db.database import get_async_session
from app.auth.tokens import get_current_user
from app.shortener import utils as shortener_utils
from app.core.logger import logger

router = APIRouter(prefix="/shortener", tags=["URL Shortener"])

@router.post("/create")
async def create_short_url(
    url_data: schemas.URLCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    # Use custom alias or generate random short code
    short_code = url_data.custom_alias or await shortener_utils.generate_unique_short_code(db)

    # Check if alias already exists
    stmt = select(models.URL).where(models.URL.short_code == short_code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Custom alias already taken."
        )

    new_url = models.URL(
        user_id=current_user.id,
        original_url=url_data.original_url,
        short_code=short_code,
        expires_at=url_data.expires_at,
        click_limit=url_data.click_limit
    )

    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)

    return new_url