from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models, schemas
from app.db.database import get_async_session
from app.auth.deps import get_current_user
from app.core.logger import logger
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/urls", tags=["URL Management"])

def generate_short_code(length: int = 6) -> str:
    """Generate a random short code."""
    return secrets.token_urlsafe(length)[:length]

@router.post("/create", response_model=schemas.URLCreateResponse)
async def create_short_url(
    url_data: schemas.URLCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    # Generate unique short code
    while True:
        short_code = generate_short_code()
        result = await db.execute(select(models.URL).where(models.URL.short_code == short_code))
        if not result.scalar_one_or_none():
            break

    # Calculate expiration time if provided
    expires_at = None
    if url_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=url_data.expires_in_days)

    # Create URL record
    new_url = models.URL(
        user_id=current_user.id,
        original_url=url_data.original_url,
        short_code=short_code,
        expires_at=expires_at,
        click_limit=url_data.click_limit
    )
    
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)

    logger.info(f"🔗 Created short URL: {short_code} for user: {current_user.email}")
    return new_url

@router.get("/list", response_model=list[schemas.URLListResponse])
async def list_user_urls(
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.URL)
        .where(models.URL.user_id == current_user.id)
        .order_by(models.URL.created_at.desc())
    )
    urls = result.scalars().all()
    return urls

@router.get("/{short_code}/stats", response_model=schemas.URLStatsResponse)
async def get_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    # Get URL and verify ownership
    result = await db.execute(
        select(models.URL)
        .where(models.URL.short_code == short_code)
        .where(models.URL.user_id == current_user.id)
    )
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found or access denied")

    # Get click logs
    result = await db.execute(
        select(models.ClickLog)
        .where(models.ClickLog.url_id == url.id)
        .order_by(models.ClickLog.clicked_at.desc())
    )
    clicks = result.scalars().all()

    return {
        "url": url,
        "clicks": clicks,
        "total_clicks": len(clicks)
    } 