import asyncio
from typing import Coroutine, Any

def run_async(coro: Coroutine) -> Any:
    """Wrapper to run async database services inside synchronous Celery Tasks."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(coro)
