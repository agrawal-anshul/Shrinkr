import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.logger import logger
from app.db.migrations import run_migrations
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()  # loads .env file

# append custom PYTHONPATH to sys.path
python_path = os.getenv("PYTHONPATH")
if python_path and python_path not in sys.path:
    sys.path.append(python_path)


app = FastAPI(
    title="Shrinkr+",
    description="""
    ## Shrinkr+ URL Shortener API
    
    A production-grade URL shortener with analytics, QR codes, and more.
    
    ### Features
    
    * **URL Shortening**: Create short links with custom aliases and expiration
    * **Analytics**: Track clicks, devices, browsers, and geographic data
    * **User Management**: Register, login, and manage shortened URLs
    * **QR Codes**: Generate QR codes for your shortened URLs
    * **Caching**: Redis-based caching for high performance
    
    ### Authentication
    
    All endpoints except for redirect require authentication via bearer token.
    Register or login to obtain your token.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations for user registration, login, and profile management"
        },
        {
            "name": "URL Management",
            "description": "Create, update, delete and manage shortened URLs"
        },
        {
            "name": "Redirect",
            "description": "URL redirection with analytics tracking"
        },
        {
            "name": "Analytics",
            "description": "Detailed analytics and statistics for shortened URLs"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # 👈 Your Angular frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Run tasks when the application starts.
    - Execute database migrations
    - Initialize any required services
    """
    # Run database migrations
    await run_migrations()
    logger.info("✅ Database migrations completed")

app.include_router(api_router)

@app.get("/", 
    summary="API root",
    description="Check if the API is running properly."
)
async def root():
    """
    Root endpoint to verify the API is running.
    
    Returns:
        A simple message indicating the API is live.
    """
    logger.info("Root pinged ✅")
    return {"message": "Shrinkr+ is live 🚀"}