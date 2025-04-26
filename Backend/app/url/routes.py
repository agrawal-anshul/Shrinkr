from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.db import models, schemas
from app.db.database import get_async_session
from app.auth.deps import get_current_user
from app.core.logger import logger
from app.core.rate_limiter import rate_limiter
from app.core.config import settings
from app.cache.redis_handler import invalidate_url_cache
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
from PIL import Image

router = APIRouter(prefix="/urls", tags=["URL Management"])

def generate_short_code(length: int = None) -> str:
    """
    Generate a random short code for URL shortening.
    
    Args:
        length: The length of the generated code (default from settings)
        
    Returns:
        A URL-safe string of the specified length
    """
    length = length or settings.DEFAULT_URL_CODE_LENGTH
    if length > settings.MAX_URL_CODE_LENGTH:
        length = settings.MAX_URL_CODE_LENGTH
    return secrets.token_urlsafe(length)[:length]

@router.post(
    "/create", 
    response_model=schemas.URLCreateResponse,
    summary="Create a shortened URL",
    description="Creates a new shortened URL with optional customization options."
)
async def create_short_url(
    request: Request,
    url_data: schemas.URLCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new shortened URL.
    
    Parameters:
    - **url_data**: Contains the original URL and optional customization settings
      - original_url: The URL to be shortened
      - custom_alias: Optional custom short code
      - expires_in_days: Days until the URL expires
      - click_limit: Maximum number of times the URL can be accessed
    
    Returns:
    - URL object with the generated short code and other metadata
    
    Raises:
    - HTTPException: For rate limit or validation errors
    """
    try:
        # Check rate limit
        await rate_limiter.check_rate_limit(request, limit=50, window=3600)  # 50 requests per hour

        # Check daily limit
        result = await db.execute(
            select(func.count(models.URL.id))
            .where(models.URL.user_id == current_user.id)
            .where(models.URL.created_at >= datetime.utcnow() - timedelta(days=1))
        )
        daily_count = result.scalar_one()
        if daily_count >= settings.MAX_DAILY_USER_URLS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily URL creation limit of {settings.MAX_DAILY_USER_URLS} exceeded"
            )

        # If custom alias is provided, check if it's available
        if url_data.custom_alias:
            # Check if custom alias is valid
            if len(url_data.custom_alias) > settings.MAX_CUSTOM_ALIAS_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Custom alias cannot exceed {settings.MAX_CUSTOM_ALIAS_LENGTH} characters"
                )
                
            result = await db.execute(
                select(models.URL).where(models.URL.short_code == url_data.custom_alias)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Custom alias already in use"
                )
            short_code = url_data.custom_alias
        else:
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
            original_url=str(url_data.original_url),
            short_code=short_code,
            expires_at=expires_at,
            click_limit=url_data.click_limit
        )
        
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)

        logger.info(f"🔗 Created short URL: {short_code} for user: {current_user.email}")
        return new_url
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error creating URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"❌ Error creating URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the URL"
        )

@router.post(
    "/bulk-create", 
    response_model=schemas.BulkURLCreateResponse,
    summary="Create multiple URLs in batch",
    description="Create multiple shortened URLs in a single API call."
)
async def bulk_create_urls(
    request: Request,
    urls_data: schemas.BulkURLCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create multiple shortened URLs in a single request.
    
    Parameters:
    - **urls_data**: Contains a list of URL objects to be created
      - urls: List of URL create objects with original URLs and options
    
    Returns:
    - A response with successfully created URLs and any failed ones
    
    Raises:
    - HTTPException: For rate limiting or validation errors
    """
    try:
        # Check rate limit
        await rate_limiter.check_rate_limit(request, limit=10, window=3600)  # 10 bulk creates per hour

        # Limit batch size
        if len(urls_data.urls) > settings.MAX_BULK_URLS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.MAX_BULK_URLS} URLs allowed per batch"
            )

        # Check daily limit
        result = await db.execute(
            select(func.count(models.URL.id))
            .where(models.URL.user_id == current_user.id)
            .where(models.URL.created_at >= datetime.utcnow() - timedelta(days=1))
        )
        daily_count = result.scalar_one()
        total_after = daily_count + len(urls_data.urls)
        
        if total_after > settings.MAX_DAILY_USER_URLS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"This batch would exceed your daily limit of {settings.MAX_DAILY_USER_URLS} URLs. You can create {settings.MAX_DAILY_USER_URLS - daily_count} more URLs today."
            )

        created_urls = []
        failed_urls = []

        for url_data in urls_data.urls:
            try:
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
                    original_url=str(url_data.original_url),
                    short_code=short_code,
                    expires_at=expires_at,
                    click_limit=url_data.click_limit
                )
                
                db.add(new_url)
                await db.commit()
                await db.refresh(new_url)
                created_urls.append(new_url)
            except Exception as e:
                await db.rollback()
                failed_urls.append({
                    "url": str(url_data.original_url),
                    "error": str(e)
                })

        logger.info(f"🔗 Bulk created {len(created_urls)} URLs for user: {current_user.email}")
        return {
            "urls": created_urls,
            "failed_urls": failed_urls
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error bulk creating URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the bulk URL creation"
        )

@router.get(
    "/list", 
    response_model=List[schemas.URLListResponse],
    summary="List user's URLs",
    description="Retrieve all shortened URLs created by the authenticated user."
)
async def list_user_urls(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all shortened URLs belonging to the current user.
    
    Returns:
    - A list of URL objects ordered by creation date (newest first)
    
    Raises:
    - HTTPException: For rate limiting
    """
    try:
        # Check rate limit
        await rate_limiter.check_rate_limit(request, limit=100, window=3600)  # 100 requests per hour

        result = await db.execute(
            select(models.URL)
            .where(models.URL.user_id == current_user.id)
            .order_by(models.URL.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        urls = result.scalars().all()
        return urls
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error listing URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the URLs"
        )

@router.get(
    "/{short_code}/stats", 
    response_model=schemas.URLStatsResponse,
    summary="Get URL statistics", 
    description="Retrieve basic statistics for a specific shortened URL."
)
async def get_url_stats(
    short_code: str = Path(..., description="The short code of the URL"),
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get basic usage statistics for a specific shortened URL.
    
    Parameters:
    - **short_code**: The short code of the URL to retrieve stats for
    
    Returns:
    - URL details along with click history and total clicks
    
    Raises:
    - HTTPException: If URL not found or unauthorized access
    """
    try:
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
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving URL stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving URL statistics"
        )

@router.patch(
    "/{short_code}", 
    response_model=schemas.URLCreateResponse,
    summary="Update a URL",
    description="Update properties of an existing shortened URL."
)
async def update_url(
    short_code: str = Path(..., description="The short code of the URL to update"),
    url_data: schemas.URLUpdate = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing shortened URL.
    
    Parameters:
    - **short_code**: The short code of the URL to update
    - **url_data**: The data to be updated (original URL, expiration, click limit)
    
    Returns:
    - The updated URL object
    
    Raises:
    - HTTPException: If URL not found or unauthorized access
    """
    try:
        if url_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )

        # Get URL and verify ownership
        result = await db.execute(
            select(models.URL)
            .where(models.URL.short_code == short_code)
            .where(models.URL.user_id == current_user.id)
        )
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(status_code=404, detail="URL not found or access denied")

        # Keep original URL for cache invalidation if it was changed
        original_url_changed = False
        if url_data.original_url is not None and url_data.original_url != url.original_url:
            original_url_changed = True

        # Update URL properties
        if url_data.original_url is not None:
            url.original_url = url_data.original_url
        if url_data.click_limit is not None:
            url.click_limit = url_data.click_limit
        if url_data.expires_in_days is not None:
            url.expires_at = datetime.utcnow() + timedelta(days=url_data.expires_in_days)
        elif url_data.expires_at is not None:
            url.expires_at = url_data.expires_at

        await db.commit()
        await db.refresh(url)

        # Invalidate cache if the original URL was changed
        if original_url_changed:
            await invalidate_url_cache(short_code)
            logger.info(f"🔄 Invalidated cache for updated URL: {short_code}")

        logger.info(f"🔄 Updated URL: {short_code} for user: {current_user.email}")
        return url
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error updating URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"❌ Error updating URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the URL"
        )

@router.delete(
    "/{short_code}",
    summary="Delete a URL",
    description="Permanently delete a shortened URL."
)
async def delete_url(
    short_code: str = Path(..., description="The short code of the URL to delete"),
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a shortened URL.
    
    Parameters:
    - **short_code**: The short code of the URL to delete
    
    Returns:
    - A success message
    
    Raises:
    - HTTPException: If URL not found or unauthorized access
    """
    try:
        # Get URL and verify ownership
        result = await db.execute(
            select(models.URL)
            .where(models.URL.short_code == short_code)
            .where(models.URL.user_id == current_user.id)
        )
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(status_code=404, detail="URL not found or access denied")

        # Delete URL
        await db.delete(url)
        await db.commit()
        
        # Invalidate cache
        await invalidate_url_cache(short_code)

        logger.info(f"🗑️ Deleted URL: {short_code} for user: {current_user.email}")
        return {"message": "URL deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error deleting URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"❌ Error deleting URL: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the URL"
        )

@router.get(
    "/{short_code}/qr",
    summary="Generate QR code",
    description="Generate a QR code for a shortened URL.",
    response_class=StreamingResponse
)
async def generate_qr_code(
    short_code: str = Path(..., description="The short code of the URL"),
    request: Request = None,
    size: int = Query(
        default=settings.QR_CODE_DEFAULT_SIZE, 
        ge=settings.QR_CODE_MIN_SIZE, 
        le=settings.QR_CODE_MAX_SIZE, 
        description=f"QR code box size ({settings.QR_CODE_MIN_SIZE}-{settings.QR_CODE_MAX_SIZE})"
    ),
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a QR code for a shortened URL.
    
    Parameters:
    - **short_code**: The short code of the URL to generate a QR code for
    - **size**: Box size for the QR code (default: 10)
    
    Returns:
    - A PNG image of the QR code
    
    Raises:
    - HTTPException: If URL not found, unauthorized access, or QR code generation fails
    """
    try:
        # Check rate limit
        if request:
            await rate_limiter.check_rate_limit(request, limit=50, window=3600)

        # Get URL and verify ownership
        result = await db.execute(
            select(models.URL)
            .where(models.URL.short_code == short_code)
            .where(models.URL.user_id == current_user.id)
        )
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(status_code=404, detail="URL not found or access denied")

        # Get base URL for redirection
        base_url = "http://localhost:8000/"
        if request:
            base_url = str(request.base_url)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(f"{base_url}redirect/{short_code}")
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr)
        img_byte_arr.seek(0)

        logger.info(f"📱 Generated QR code for URL: {short_code}")
        return StreamingResponse(img_byte_arr, media_type="image/png")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error generating QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code"
        ) 