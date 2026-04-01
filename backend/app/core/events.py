import json
import logging
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Single Redis client instance for Pub/Sub
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class EventPublisher:
    @staticmethod
    async def publish(channel: str, message: dict):
        try:
            payload = json.dumps(message)
            await redis_client.publish(channel, payload)
            logger.info(f"Published event to {channel}: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish event to {channel}: {e}")

publisher = EventPublisher()
