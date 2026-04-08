import json
from datetime import datetime
from uuid import UUID
from typing import Any, Dict
from backend.src.infrastructure.redis import redis_client

class InventoryEventPublisher:
    @staticmethod
    async def publish(event_type: str, aggregate_id: UUID, payload: Dict[str, Any]):
        event = {
            "event_id": str(UUID(int=datetime.utcnow().microsecond)), # Simplified UUID
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "aggregate_id": str(aggregate_id),
            "payload": json.dumps(payload),
            "metadata": json.dumps({"source": "InventoryContext"})
        }
        
        # Publish to Redis Stream
        await redis_client.xadd("citms:inventory:events", event, maxlen=100000)

    @staticmethod
    async def publish_license_violation(license_id: UUID, software_name: str, used: int, total: int):
        payload = {
            "license_id": str(license_id),
            "software_name": software_name,
            "used_seats": used,
            "total_seats": total
        }
        await redis_client.xadd("citms:license:events", {
            "event_type": "LICENSE_VIOLATED",
            "payload": json.dumps(payload)
        })
