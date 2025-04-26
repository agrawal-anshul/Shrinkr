from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models, schemas
from app.db.database import get_async_session
from app.auth.deps import get_current_user
from app.core.logger import logger
from app.core.rate_limiter import rate_limiter
from app.core.config import settings
from app.analytics.service import AnalyticsService
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get(
    "/urls/{short_code}/detailed", 
    response_model=schemas.DetailedAnalytics,
    summary="Get detailed analytics",
    description="Retrieve comprehensive analytics data for a specific shortened URL."
)
async def get_detailed_analytics(
    short_code: str,
    days: Optional[int] = Query(
        default=settings.ANALYTICS_DEFAULT_DAYS, 
        ge=1, 
        le=settings.ANALYTICS_MAX_DAYS, 
        description=f"Number of days to include in the analytics (1-{settings.ANALYTICS_MAX_DAYS})"
    ),
    request: Request = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed analytics for a specific shortened URL.
    
    This endpoint provides comprehensive analytics including:
    - Total clicks and unique visitors
    - Time-based statistics (clicks per day)
    - Location-based statistics
    - Device, browser, and operating system breakdowns
    - Mobile vs desktop and bot percentage statistics
    
    Parameters:
    - **short_code**: The short code of the URL to get analytics for
    - **days** (optional): Number of days to include in the analytics (default: {settings.ANALYTICS_DEFAULT_DAYS}, max: {settings.ANALYTICS_MAX_DAYS})
    
    Returns:
    - Detailed analytics object with various statistics
    
    Raises:
    - HTTPException: If URL not found, unauthorized, or rate limited
    """
    try:
        # Check rate limit
        if request:
            await rate_limiter.check_rate_limit(request, limit=100, window=3600)

        # Get URL and verify ownership
        result = await db.execute(
            select(models.URL)
            .where(models.URL.short_code == short_code)
            .where(models.URL.user_id == current_user.id)
        )
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(status_code=404, detail="URL not found or access denied")

        # Get analytics
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_detailed_analytics(url.id, days)

        logger.info(f"📊 Generated detailed analytics for URL: {short_code}")
        return analytics
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error generating analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating analytics"
        )

@router.get(
    "/urls/{short_code}/export",
    summary="Export analytics data",
    description="Export complete analytics data and raw click logs for a shortened URL in JSON format."
)
async def export_analytics(
    short_code: str,
    days: Optional[int] = Query(
        default=settings.ANALYTICS_DEFAULT_DAYS, 
        ge=1, 
        le=settings.ANALYTICS_MAX_DAYS, 
        description=f"Number of days to include in the export (1-{settings.ANALYTICS_MAX_DAYS})"
    ),
    request: Request = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Export complete analytics data for a shortened URL.
    
    This endpoint provides a downloadable JSON file containing:
    - URL details
    - Processed analytics (all statistics)
    - Raw click logs for detailed analysis
    
    Parameters:
    - **short_code**: The short code of the URL to export analytics for
    - **days** (optional): Number of days to include in the export (default: {settings.ANALYTICS_DEFAULT_DAYS}, max: {settings.ANALYTICS_MAX_DAYS})
    
    Returns:
    - JSON file attachment with complete analytics data
    
    Raises:
    - HTTPException: If URL not found, unauthorized, or rate limited
    """
    try:
        # Check rate limit
        if request:
            await rate_limiter.check_rate_limit(request, limit=10, window=3600)

        # Get URL and verify ownership
        result = await db.execute(
            select(models.URL)
            .where(models.URL.short_code == short_code)
            .where(models.URL.user_id == current_user.id)
        )
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(status_code=404, detail="URL not found or access denied")

        # Get analytics export
        analytics_service = AnalyticsService(db)
        export_data = await analytics_service.export_analytics(url.id, days)

        # Convert to JSON
        json_data = json.dumps(export_data.dict(), default=str)

        logger.info(f"📥 Exported analytics for URL: {short_code}")
        return JSONResponse(
            content=json.loads(json_data),  # Parse back to ensure valid JSON
            headers={
                "Content-Disposition": f'attachment; filename="analytics_{short_code}_{datetime.utcnow().strftime("%Y%m%d")}.json"'
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error exporting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while exporting analytics"
        )
