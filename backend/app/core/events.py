import json
import logging
from redis.asyncio import Redis
from typing import Optional

from app.core.config import settings
from app.core.audit_context import request_id

logger = logging.getLogger(__name__)

# Single Redis client instance for Pub/Sub and Streams
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class EventPublisher:
    @staticmethod
    async def publish(channel: str, message: dict):
        """Standard ephemeral Pub/Sub (Module 7 logic)"""
        try:
            payload = json.dumps(message)
            await redis_client.publish(channel, payload)
            logger.info(f"Published event to {channel}: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish event to {channel}: {e}")

    @staticmethod
    async def add_stream(stream_key: str, data: dict, maxlen: Optional[int] = 10000):
        """
        v3.6 §2.3: Durable Redis Streams for Enterprise events.
        Includes trace_id automatically for end-to-end correlation.
        """
        try:
            # Enforce trace_id for stream events
            trace_id = request_id.get()
            if trace_id:
                data["trace_id"] = str(trace_id)
            
            # Redis Streams expect string keys/values
            # xadd(name, fields, id, maxlen, approximate)
            await redis_client.xadd(stream_key, data, maxlen=maxlen, approximate=True)
            logger.info(f"Added event to stream {stream_key}")
        except Exception as e:
            logger.error(f"Failed to add event to stream {stream_key}: {e}")

publisher = EventPublisher()
