from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import models, schemas
from app.db.database import async_session
from app.auth.utils import hash_password, verify_password
from app.auth.tokens import create_access_token
from app.core.logger import logger
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut)
async def register_user(user_data: schemas.UserCreate, db: AsyncSession = Depends(async_session)):
    # Check if user already exists
    result = await db.execute(select(models.User).where(models.User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = hash_password(user_data.password)
    new_user = models.User(email=user_data.email, password_hash=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"🆕 Registered user: {new_user.email}")
    return new_user


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(async_session),
):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id)})

    logger.info(f"✅ Logged in: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


from app.auth.deps import get_current_user

@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user