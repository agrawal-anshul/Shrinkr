from fastapi import HTTPException, Request, status
from redis import Redis
from redis.exceptions import RedisError
from datetime import datetime, timedelta
import json
from app.core.config import settings
from app.core.logger import logger

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_limit = 100  # requests per window
        self.default_window = 3600  # 1 hour in seconds

    async def check_rate_limit(self, request: Request = None, limit: int = None, window: int = None):
        """
        Check if the request has hit rate limits.
        
        Args:
            request: The FastAPI request object
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        try:
            # If request is None, skip rate limiting
            if request is None:
                return True
            
            # Get client IP
            client_ip = "127.0.0.1"
            if request.client and hasattr(request.client, 'host'):
                client_ip = request.client.host
            
            # Use default values if not specified
            limit = limit or self.default_limit
            window = window or self.default_window

            # Create a unique key for this IP
            key = f"rate_limit:{client_ip}"

            # Get current count
            current = self.redis.get(key)
            
            if current is None:
                # First request, set counter and expiry
                self.redis.setex(key, window, 1)
                return True
            
            current = int(current)
            
            if current >= limit:
                # Get TTL to show when the limit resets
                ttl = self.redis.ttl(key)
                reset_time = datetime.now() + timedelta(seconds=ttl)
                reset_time_str = reset_time.strftime("%H:%M:%S")
                
                logger.warning(f"⛔ Rate limit exceeded for {client_ip}: {current}/{limit} requests")
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "reset_in_seconds": ttl,
                        "reset_at": reset_time_str,
                        "limit": limit,
                        "window_seconds": window
                    }
                )
            
            # Increment counter
            self.redis.incr(key)
            return True
        except RedisError as e:
            # Log the error but don't block the request if Redis is down
            logger.error(f"❌ Redis error in rate limiter: {str(e)}")
            return True
        except Exception as e:
            # Log other errors but don't block the request
            logger.error(f"❌ Unexpected error in rate limiter: {str(e)}")
            return True

# Create a singleton instance
try:
    rate_limiter = RateLimiter(Redis.from_url(settings.REDIS_URL))
    logger.info("✅ Rate limiter initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize rate limiter: {str(e)}")
    # Create a dummy rate limiter that always allows requests
    class DummyRateLimiter:
        async def check_rate_limit(self, *args, **kwargs):
            return True
    rate_limiter = DummyRateLimiter() 