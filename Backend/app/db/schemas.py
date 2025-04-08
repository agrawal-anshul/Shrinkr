from pydantic import BaseModel, HttpUrl, EmailStr, validator
from typing import Optional, List
from datetime import datetime

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
        orm_mode = True

# -------------------------------
# URL Schemas
# -------------------------------

class URLBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    click_limit: Optional[int] = None

class URLCreate(URLBase):
    pass

class URLResponse(BaseModel):
    id: int
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int

    class Config:
        orm_mode = True

# -------------------------------
# Click Log Schema
# -------------------------------

class ClickLogResponse(BaseModel):
    clicked_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    referrer: Optional[str]

    class Config:
        orm_mode = True