from pydantic import BaseModel, HttpUrl, EmailStr, field_validator, AnyHttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

# -------------------------------
# Auth Schemas
# -------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# -------------------------------
# User Schemas
# -------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------
# URL Schemas
# -------------------------------

class URLBase(BaseModel):
    original_url: AnyHttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    click_limit: Optional[int] = None

    @field_validator('custom_alias')
    @classmethod
    def validate_custom_alias(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('custom_alias must be at least 3 characters long')
            if len(v) > 20:
                raise ValueError('custom_alias must be at most 20 characters long')
            if not v.isalnum():
                raise ValueError('custom_alias must contain only alphanumeric characters')
        return v

    @field_validator('click_limit')
    @classmethod
    def validate_click_limit(cls, v):
        if v is not None and v < 0:
            raise ValueError('click_limit must be positive')
        return v

class URLCreate(URLBase):
    expires_in_days: Optional[int] = None

class URLUpdate(BaseModel):
    original_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    click_limit: Optional[int] = None
    expires_in_days: Optional[int] = None

    @field_validator('expires_in_days')
    @classmethod
    def validate_expires_in_days(cls, v):
        if v is not None and v < 0:
            raise ValueError('expires_in_days must be positive')
        return v

class URLCreateResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    click_limit: Optional[int]

    class Config:
        from_attributes = True

class URLListResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    click_limit: Optional[int]

    class Config:
        from_attributes = True

class URLStatsResponse(BaseModel):
    url: URLListResponse
    clicks: List['ClickLogResponse']
    total_clicks: int

    class Config:
        from_attributes = True

class BulkURLCreate(BaseModel):
    urls: List[URLCreate]

class BulkURLCreateResponse(BaseModel):
    urls: List[URLCreateResponse]
    failed_urls: List[dict]

# -------------------------------
# Click Log Schema
# -------------------------------

class ClickLogResponse(BaseModel):
    clicked_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    is_mobile: Optional[bool] = False
    is_bot: Optional[bool] = False

    class Config:
        from_attributes = True

# -------------------------------
# Analytics Schemas
# -------------------------------

class TimeBasedStats(BaseModel):
    date: str
    clicks: int

class LocationStats(BaseModel):
    country: str = "Unknown"  # Default to "Unknown" if null
    city: Optional[str] = None
    clicks: int

class DeviceStats(BaseModel):
    device_type: str = "Unknown"  # Default to "Unknown" if null
    clicks: int

class BrowserStats(BaseModel):
    browser: str = "Unknown"  # Default to "Unknown" if null
    clicks: int

class OSStats(BaseModel):
    os: str = "Unknown"  # Default to "Unknown" if null
    clicks: int

class DetailedAnalytics(BaseModel):
    total_clicks: int
    unique_visitors: int
    time_based: List[TimeBasedStats]
    locations: List[LocationStats]
    devices: List[DeviceStats]
    browsers: List[BrowserStats]
    operating_systems: List[OSStats]
    is_mobile_percentage: float
    is_bot_percentage: float

class AnalyticsExport(BaseModel):
    url: URLListResponse
    analytics: DetailedAnalytics
    raw_clicks: List[ClickLogResponse]

    class Config:
        from_attributes = True