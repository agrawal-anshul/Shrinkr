from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.db import models
from app.db.database import async_session
from app.core.logger import logger
from app.cache.redis_handler import get_cached_url, set_cached_url

router = APIRouter(tags=["Redirect"])

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(async_session)
):
    # Try cache
    cached_url = await get_cached_url(short_code)
    if cached_url:
        logger.info(f"⚡ Cache hit: {short_code}")
        return RedirectResponse(cached_url)

    # Fallback: look up in DB
    stmt = select(models.URL).where(models.URL.short_code == short_code)
    result = await db.execute(stmt)
    url: models.URL = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Check if expired
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This short URL has expired")

    # Check click limit
    if url.click_limit is not None and url.click_count >= url.click_limit:
        raise HTTPException(status_code=410, detail="Click limit exceeded")

    # Log the click
    db.add(models.ClickLog(
        url_id=url.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    ))

    # Update click count
    url.click_count += 1
    await db.commit()

    # Cache it
    await set_cached_url(short_code, url.original_url)

    logger.info(f"🔁 Redirected /{short_code} → {url.original_url}")
    return RedirectResponse(url.original_url)