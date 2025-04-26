from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db import models, schemas
from app.db.database import get_async_session
from app.auth.utils import hash_password, verify_password
from app.auth.tokens import create_access_token
from app.core.logger import logger
from app.core.rate_limiter import rate_limiter
from fastapi.security import OAuth2PasswordRequestForm
import traceback
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register", 
    response_model=schemas.TokenResponse,
    summary="Register a new user",
    description="Create a new user account and return an access token."
)
async def register_user(
    request: Request,
    user_data: schemas.UserCreate, 
    db: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user account.
    
    Parameters:
    - **user_data**: User registration data
      - email: User's email address
      - password: User's password (will be hashed)
    
    Returns:
    - JWT access token for immediate authentication
    
    Raises:
    - HTTPException: If the email is already registered
    """
    try:
        # Apply rate limiting to prevent abuse
        await rate_limiter.check_rate_limit(request, limit=5, window=60)  # 5 registrations per minute

        # Validate email format (already done by Pydantic)
        # Validate password requirements
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )

        # Check if user already exists
        result = await db.execute(select(models.User).where(models.User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Don't leak information about registered emails
            logger.warning(f"🛑 Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        hashed_pw = hash_password(user_data.password)
        new_user = models.User(email=user_data.email, password_hash=hashed_pw)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(new_user.id)},
            expires_delta=timedelta(days=1)  # Token expires in 1 day
        )

        logger.info(f"🆕 Registered user: {new_user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error during registration: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during registration: {str(e)}\n{traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/login", 
    response_model=schemas.TokenResponse,
    summary="User login",
    description="Authenticate a user and return an access token."
)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Authenticate a user and generate an access token.
    
    Parameters:
    - **form_data**: OAuth2 password request form data
      - username: User's email address
      - password: User's password
    
    Returns:
    - JWT access token for authentication
    
    Raises:
    - HTTPException: If login credentials are invalid
    """
    try:
        # Apply rate limiting to prevent brute force
        client_ip = request.client.host if request.client else "unknown"
        await rate_limiter.check_rate_limit(request, limit=10, window=60)  # 10 login attempts per minute

        # Validate credentials
        result = await db.execute(select(models.User).where(models.User.email == form_data.username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(form_data.password, user.password_hash):
            logger.warning(f"🔒 Failed login attempt for: {form_data.username} from {client_ip}")
            # Use a generic error message to not leak information about registered emails
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=1)  # Token expires in 1 day
        )

        logger.info(f"✅ Logged in: {user.email} from {client_ip}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


from app.auth.deps import get_current_user

@router.get(
    "/me", 
    response_model=schemas.UserOut,
    summary="Get current user",
    description="Retrieve the current authenticated user's information."
)
async def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    
    Returns:
    - User object with profile information
    
    Raises:
    - HTTPException: If the user is not authenticated (handled by dependency)
    """
    try:
        return current_user
    except Exception as e:
        logger.error(f"❌ Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while retrieving user profile"
        )