import redis.asyncio as redis
from backend.src.core.config import settings

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

async def get_redis():
    return redis_client
