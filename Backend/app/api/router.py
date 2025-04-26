from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.redirect.routes import router as redirect_router
from app.url.routes import router as url_router
from app.analytics.routes import router as analytics_router

router = APIRouter()

# Include route modules
router.include_router(auth_router)
router.include_router(redirect_router)
router.include_router(url_router)
router.include_router(analytics_router)