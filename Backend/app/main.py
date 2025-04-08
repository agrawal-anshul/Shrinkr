import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.logger import logger


load_dotenv()  # loads .env file

# append custom PYTHONPATH to sys.path
python_path = os.getenv("PYTHONPATH")
if python_path and python_path not in sys.path:
    sys.path.append(python_path)

app = FastAPI(
    title="Shrinkr+",
    description="Production-grade URL shortener",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/")
async def root():
    logger.info("Root pinged ✅")
    return {"message": "Shrinkr+ is live 🚀"}