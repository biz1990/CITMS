"""
app/core/cache.py — Redis async cache helper for Module 8 Reports.

Usage:
    from app.core.cache import cache

    data = await cache.get("my_key")
    await cache.set("my_key", {"foo": "bar"}, ttl=900)
    await cache.delete_pattern("report:ram*")
"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level client (lazily initialised on first use or at startup)
# ---------------------------------------------------------------------------
_client: aioredis.Redis | None = None


def _get_client() -> aioredis.Redis:
    """Return the shared Redis client, creating it if necessary."""
    global _client
    if _client is None:
        _client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


# ---------------------------------------------------------------------------
# Lifecycle helpers (call from FastAPI lifespan / startup event)
# ---------------------------------------------------------------------------
async def connect() -> None:
    """Warm up the connection pool."""
    client = _get_client()
    await client.ping()
    logger.info("Redis cache connected: %s", settings.REDIS_URL)


async def disconnect() -> None:
    """Gracefully close the connection pool."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("Redis cache disconnected.")


# ---------------------------------------------------------------------------
# Public cache API
# ---------------------------------------------------------------------------
class _Cache:
    """Thin wrapper around redis.asyncio providing JSON serialisation."""

    # Default TTL for Module 8 aggregate reports (15 minutes)
    DEFAULT_TTL: int = 900

    # Key prefix so all report keys can be flushed together
    PREFIX: str = "citms:report"

    # ------------------------------------------------------------------ #
    # Core operations
    # ------------------------------------------------------------------ #
    async def get(self, key: str) -> Any | None:
        try:
            raw = await _get_client().get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache GET failed for key=%s: %s", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
        try:
            serialized = json.dumps(value, default=str)
            await _get_client().setex(key, ttl, serialized)
        except Exception as exc:
            logger.warning("Cache SET failed for key=%s: %s", key, exc)

    async def delete(self, key: str) -> None:
        try:
            await _get_client().delete(key)
        except Exception as exc:
            logger.warning("Cache DELETE failed for key=%s: %s", key, exc)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching *pattern* (uses SCAN, safe on large DBs)."""
        try:
            client = _get_client()
            deleted = 0
            async for key in client.scan_iter(match=pattern, count=100):
                await client.delete(key)
                deleted += 1
            logger.info("Cache purged %d keys matching pattern=%s", deleted, pattern)
            return deleted
        except Exception as exc:
            logger.warning("Cache DELETE_PATTERN failed: %s", exc)
            return 0

    # ------------------------------------------------------------------ #
    # Key builder helpers
    # ------------------------------------------------------------------ #
    def make_key(self, report_type: str, filters: dict) -> str:
        """
        Build a deterministic cache key for a report + filter combination.

        Pattern: citms:report:{report_type}:{sha256_of_sorted_filters}

        Example:
            citms:report:ram_inventory:a3f92c...
        """
        # Sort so that {dept: "IT", mfr: "Samsung"} == {mfr: "Samsung", dept: "IT"}
        canonical = json.dumps(
            {k: str(v) for k, v in sorted(filters.items()) if v is not None},
            sort_keys=True,
        )
        digest = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return f"{self.PREFIX}:{report_type}:{digest}"

    def invalidation_pattern(self, report_type: str) -> str:
        """Pattern used to flush all cached variants of a report type."""
        return f"{self.PREFIX}:{report_type}:*"


# Singleton instance — import this everywhere
cache = _Cache()
