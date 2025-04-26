from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.core.config import settings
from app.core.logger import logger
import json

# Initialize Redis client
redis = None

async def get_redis():
    """Get a Redis connection"""
    global redis
    if redis is None:
        try:
            redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test the connection
            await redis.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection error: {str(e)}")
            return None
    return redis

async def get_cached_url(short_code: str) -> str:
    """
    Get a URL from cache by short code
    
    Args:
        short_code: The short code to look up
        
    Returns:
        The original URL if found, None otherwise
    """
    try:
        r = await get_redis()
        if not r:
            return None
            
        return await r.get(f"url:{short_code}")
    except RedisError as e:
        logger.error(f"❌ Redis error getting URL {short_code}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error getting cached URL: {str(e)}")
        return None

async def set_cached_url(short_code: str, original_url: str, ttl_seconds: int = None):
    """
    Cache a URL with its short code
    
    Args:
        short_code: The short code
        original_url: The original URL to cache
        ttl_seconds: Time-to-live in seconds (default from settings)
    """
    try:
        r = await get_redis()
        if not r:
            return
            
        ttl = ttl_seconds or settings.REDIS_CACHE_TTL
        await r.set(f"url:{short_code}", original_url, ex=ttl)
        logger.debug(f"🔄 Cached URL {short_code} for {ttl} seconds")
    except RedisError as e:
        logger.error(f"❌ Redis error caching URL {short_code}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error caching URL: {str(e)}")

async def invalidate_url_cache(short_code: str):
    """
    Remove a URL from cache
    
    Args:
        short_code: The short code to remove
    """
    try:
        r = await get_redis()
        if not r:
            return
            
        await r.delete(f"url:{short_code}")
        logger.debug(f"🗑️ Removed URL {short_code} from cache")
    except RedisError as e:
        logger.error(f"❌ Redis error invalidating URL {short_code}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error invalidating URL cache: {str(e)}")

async def cache_json(key: str, data: dict, ttl_seconds: int = None):
    """
    Cache JSON data
    
    Args:
        key: The cache key
        data: The data to cache
        ttl_seconds: Time-to-live in seconds (default from settings)
    """
    try:
        r = await get_redis()
        if not r:
            return
            
        ttl = ttl_seconds or settings.REDIS_CACHE_TTL
        json_data = json.dumps(data)
        await r.set(key, json_data, ex=ttl)
    except RedisError as e:
        logger.error(f"❌ Redis error caching JSON for {key}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error caching JSON: {str(e)}")

async def get_cached_json(key: str):
    """
    Get JSON data from cache
    
    Args:
        key: The cache key
        
    Returns:
        The cached data dict if found, None otherwise
    """
    try:
        r = await get_redis()
        if not r:
            return None
            
        data = await r.get(key)
        if data:
            return json.loads(data)
        return None
    except RedisError as e:
        logger.error(f"❌ Redis error getting JSON for {key}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error getting cached JSON: {str(e)}")
        return None