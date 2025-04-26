from fastapi import APIRouter, Request, Depends, HTTPException, status, Path
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from ua_parser import user_agent_parser
import traceback

from app.db import models
from app.db.database import get_async_session
from app.core.logger import logger
from app.cache.redis_handler import get_cached_url, set_cached_url

router = APIRouter(tags=["Redirect"])

@router.get(
    "/{short_code}", 
    response_class=RedirectResponse,
    summary="Redirect to original URL",
    description="Redirect to the original URL associated with the short code, tracking analytics data."
)
async def redirect_to_original(
    short_code: str = Path(..., min_length=1, description="The short code of the URL to redirect to"),
    request: Request = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Redirect to the original URL associated with a short code.
    
    This endpoint performs the following operations:
    1. Check cache for the shortened URL
    2. If not in cache, look up in database
    3. Validate expiration and click limits
    4. Track analytics data (user agent, device info, etc.)
    5. Increment click count
    6. Update cache
    7. Redirect to the original URL
    
    Parameters:
    - **short_code**: The short code of the URL to redirect to
    
    Returns:
    - HTTP redirect to the original URL
    
    Raises:
    - HTTPException 404: If the short URL doesn't exist
    - HTTPException 410: If the URL has expired or click limit is exceeded
    """
    try:
        # Input validation
        if not short_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short code is required"
            )

        # Try cache first
        cached_url = await get_cached_url(short_code)
        if cached_url:
            logger.info(f"⚡ Cache hit: {short_code}")
            return RedirectResponse(cached_url)

        # Fallback: look up in DB
        stmt = select(models.URL).where(models.URL.short_code == short_code)
        result = await db.execute(stmt)
        url: models.URL = result.scalar_one_or_none()

        if not url:
            logger.warning(f"🔍 Short URL not found: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Short URL not found"
            )

        # Check if expired
        if url.expires_at and url.expires_at < datetime.now(timezone.utc):
            logger.warning(f"⏰ Expired URL accessed: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_410_GONE, 
                detail="This short URL has expired"
            )

        # Check click limit
        if url.click_limit is not None and url.click_count >= url.click_limit:
            logger.warning(f"🔢 Click limit exceeded: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_410_GONE, 
                detail="Click limit exceeded"
            )

        # Get client info
        ip_address = "127.0.0.1"  # Default in case client info is not available
        referrer = None
        user_agent_string = ""
        
        if request:
            ip_address = request.client.host if request.client else ip_address
            referrer = request.headers.get("referer")
            user_agent_string = request.headers.get("user-agent", "")

        # Parse user agent
        try:
            ua_info = user_agent_parser.Parse(user_agent_string)
        except Exception as e:
            logger.warning(f"Failed to parse user agent: {str(e)}")
            ua_info = {
                "device": {"family": "Unknown", "is_mobile": False},
                "user_agent": {"family": "Unknown"},
                "os": {"family": "Unknown"}
            }

        # Create click log
        click_log = models.ClickLog(
            url_id=url.id,
            ip_address=ip_address,
            user_agent=user_agent_string,
            referrer=referrer,
            country=None,  # TODO: Add IP geolocation
            city=None,     # TODO: Add IP geolocation
            device_type=ua_info.get("device", {}).get("family"),
            browser=ua_info.get("user_agent", {}).get("family"),
            os=ua_info.get("os", {}).get("family"),
            is_mobile=ua_info.get("device", {}).get("is_mobile", False),
            is_bot=ua_info.get("user_agent", {}).get("family") in ["Bot", "Crawler", "Spider"]
        )

        # Update click count
        url.click_count += 1
        
        try:
            db.add(click_log)
            await db.commit()
        except SQLAlchemyError as e:
            # Log the error but continue with the redirect
            logger.error(f"❌ Database error recording click: {str(e)}")
            await db.rollback()

        # Cache it for faster future access
        try:
            await set_cached_url(short_code, url.original_url)
        except Exception as e:
            # Log the error but continue with the redirect
            logger.error(f"❌ Cache error: {str(e)}")

        logger.info(f"🔁 Redirected /{short_code} → {url.original_url}")
        return RedirectResponse(url.original_url)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error during redirect: {str(e)}")
        # We still need to return something even if there's an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during redirect: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )