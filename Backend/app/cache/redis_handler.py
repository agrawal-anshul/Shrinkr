from redis.asyncio import Redis
import os
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = None

async def get_redis():
    global redis
    if redis is None:
        redis = Redis.from_url(REDIS_URL, decode_responses=True)
    return redis

async def get_cached_url(short_code: str) -> str:
    r = await get_redis()
    return await r.get(f"url:{short_code}")

async def set_cached_url(short_code: str, original_url: str, ttl_seconds: int = 3600):
    r = await get_redis()
    await r.set(f"url:{short_code}", original_url, ex=ttl_seconds)