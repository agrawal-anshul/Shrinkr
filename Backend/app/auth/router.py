from fastapi import APIRouter
from app.auth import routes as auth_routes
# from app.shortener import routes as shortener_routes
# from app.redirect import routes as redirect_routes
# from app.analytics import routes as analytics_routes

router = APIRouter()
router.include_router(auth_routes.router)
# router.include_router(shortener_routes.router)
# router.include_router(redirect_routes.router)
# router.include_router(analytics_routes.router)