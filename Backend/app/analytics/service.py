from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.db import models, schemas
from collections import Counter
import json

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_detailed_analytics(self, url_id: int, days: int = 30) -> schemas.DetailedAnalytics:
        """
        Get detailed analytics for a specific URL.
        
        Args:
            url_id: The database ID of the URL
            days: Number of days to include in the analytics
            
        Returns:
            Detailed analytics object with various statistics
        """
        try:
            # Get all clicks for the URL
            result = await self.db.execute(
                select(models.ClickLog)
                .where(models.ClickLog.url_id == url_id)
                .where(models.ClickLog.clicked_at >= datetime.utcnow() - timedelta(days=days))
            )
            clicks = result.scalars().all()

            # Handle case with no clicks
            if not clicks:
                return schemas.DetailedAnalytics(
                    total_clicks=0,
                    unique_visitors=0,
                    time_based=[],
                    locations=[],
                    devices=[],
                    browsers=[],
                    operating_systems=[],
                    is_mobile_percentage=0,
                    is_bot_percentage=0
                )

            # Calculate unique visitors
            unique_visitors = len(set(click.ip_address for click in clicks if click.ip_address))

            # Time-based stats
            time_based = self._get_time_based_stats(clicks)

            # Location stats
            locations = self._get_location_stats(clicks)

            # Device stats
            devices = self._get_device_stats(clicks)

            # Browser stats
            browsers = self._get_browser_stats(clicks)

            # OS stats
            operating_systems = self._get_os_stats(clicks)

            # Mobile and bot percentages
            total_clicks = len(clicks)
            is_mobile = sum(1 for click in clicks if click.is_mobile)
            is_bot = sum(1 for click in clicks if click.is_bot)

            return schemas.DetailedAnalytics(
                total_clicks=total_clicks,
                unique_visitors=unique_visitors,
                time_based=time_based,
                locations=locations,
                devices=devices,
                browsers=browsers,
                operating_systems=operating_systems,
                is_mobile_percentage=(is_mobile / total_clicks * 100) if total_clicks > 0 else 0,
                is_bot_percentage=(is_bot / total_clicks * 100) if total_clicks > 0 else 0
            )
        except Exception as e:
            # Log the error but return empty analytics rather than failing
            from app.core.logger import logger
            logger.error(f"Error generating analytics: {str(e)}")
            return schemas.DetailedAnalytics(
                total_clicks=0,
                unique_visitors=0,
                time_based=[],
                locations=[],
                devices=[],
                browsers=[],
                operating_systems=[],
                is_mobile_percentage=0,
                is_bot_percentage=0
            )

    def _get_time_based_stats(self, clicks: List[models.ClickLog]) -> List[schemas.TimeBasedStats]:
        """Generate time-based statistics from click logs"""
        try:
            daily_clicks = Counter()
            for click in clicks:
                date_str = click.clicked_at.strftime('%Y-%m-%d')
                daily_clicks[date_str] += 1
            
            return [
                schemas.TimeBasedStats(date=date, clicks=count)
                for date, count in sorted(daily_clicks.items())
            ]
        except Exception:
            return []

    def _get_location_stats(self, clicks: List[models.ClickLog]) -> List[schemas.LocationStats]:
        """
        Generate location-based statistics from click logs.
        Handles NULL country/city values.
        """
        try:
            # Filter out clicks with None country
            valid_clicks = [click for click in clicks if click.country is not None]
            
            # If no valid location data, return a single "Unknown" entry
            if not valid_clicks:
                return [schemas.LocationStats(country="Unknown", city=None, clicks=len(clicks))]
            
            location_clicks = Counter()
            for click in valid_clicks:
                key = (click.country or "Unknown", click.city)
                location_clicks[key] += 1
            
            return [
                schemas.LocationStats(
                    country=country or "Unknown",
                    city=city,
                    clicks=count
                )
                for (country, city), count in location_clicks.most_common()
            ]
        except Exception:
            return [schemas.LocationStats(country="Unknown", city=None, clicks=len(clicks))]

    def _get_device_stats(self, clicks: List[models.ClickLog]) -> List[schemas.DeviceStats]:
        """Generate device statistics from click logs"""
        try:
            device_clicks = Counter()
            for click in clicks:
                device = click.device_type or "Unknown"
                device_clicks[device] += 1
            
            return [
                schemas.DeviceStats(device_type=device, clicks=count)
                for device, count in device_clicks.most_common()
            ]
        except Exception:
            return [schemas.DeviceStats(device_type="Unknown", clicks=len(clicks))]

    def _get_browser_stats(self, clicks: List[models.ClickLog]) -> List[schemas.BrowserStats]:
        """Generate browser statistics from click logs"""
        try:
            browser_clicks = Counter()
            for click in clicks:
                browser = click.browser or "Unknown"
                browser_clicks[browser] += 1
            
            return [
                schemas.BrowserStats(browser=browser, clicks=count)
                for browser, count in browser_clicks.most_common()
            ]
        except Exception:
            return [schemas.BrowserStats(browser="Unknown", clicks=len(clicks))]

    def _get_os_stats(self, clicks: List[models.ClickLog]) -> List[schemas.OSStats]:
        """Generate OS statistics from click logs"""
        try:
            os_clicks = Counter()
            for click in clicks:
                os = click.os or "Unknown"
                os_clicks[os] += 1
            
            return [
                schemas.OSStats(os=os, clicks=count)
                for os, count in os_clicks.most_common()
            ]
        except Exception:
            return [schemas.OSStats(os="Unknown", clicks=len(clicks))]

    async def export_analytics(self, url_id: int, days: int = 30) -> schemas.AnalyticsExport:
        """
        Export complete analytics data for a specific URL.
        
        Args:
            url_id: The database ID of the URL
            days: Number of days to include in the export
            
        Returns:
            Export data with URL details, analytics, and raw click data
        """
        try:
            # Get URL
            result = await self.db.execute(
                select(models.URL).where(models.URL.id == url_id)
            )
            url = result.scalar_one_or_none()
            
            if not url:
                raise ValueError(f"URL with id {url_id} not found")

            # Get clicks
            result = await self.db.execute(
                select(models.ClickLog)
                .where(models.ClickLog.url_id == url_id)
                .where(models.ClickLog.clicked_at >= datetime.utcnow() - timedelta(days=days))
            )
            clicks = result.scalars().all()

            # Get analytics
            analytics = await self.get_detailed_analytics(url_id, days)

            return schemas.AnalyticsExport(
                url=url,
                analytics=analytics,
                raw_clicks=clicks
            )
        except Exception as e:
            from app.core.logger import logger
            logger.error(f"Error exporting analytics: {str(e)}")
            
            # Get URL even if analytics fail
            result = await self.db.execute(
                select(models.URL).where(models.URL.id == url_id)
            )
            url = result.scalar_one_or_none()
            
            if not url:
                raise ValueError(f"URL with id {url_id} not found")
                
            # Return minimal export with empty analytics
            empty_analytics = schemas.DetailedAnalytics(
                total_clicks=0,
                unique_visitors=0,
                time_based=[],
                locations=[],
                devices=[],
                browsers=[],
                operating_systems=[],
                is_mobile_percentage=0,
                is_bot_percentage=0
            )
            
            return schemas.AnalyticsExport(
                url=url,
                analytics=empty_analytics,
                raw_clicks=[]
            )
