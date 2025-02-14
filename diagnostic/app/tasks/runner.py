import asyncio
from typing import Any, Coroutine, Optional

from cachetools import TTLCache


class CachedTaskRunner:
    def __init__(self):
        self.is_running: bool = False
        self.result: Optional[Any] = None
        self.cache = TTLCache(maxsize=2, ttl=5)

    def set_result(self, result: Any) -> None:
        self.result = result
        self.cache["result"] = result
        self.is_running = False

    async def wait_for_result(self, max_timeout: Optional[int] = None) -> Any:
        INTERVAL = 0.5
        waits = 0
        while True:
            await asyncio.sleep(INTERVAL)
            waits += INTERVAL

            if not self.is_running:
                return self.result

            if max_timeout is not None and waits >= max_timeout:
                return self.result

    async def run_task(self, fun: Coroutine[Any, Any, Any], **kwargs) -> None:
        if self.is_running:
            return

        if cached_result := self.cache.get("result"):
            return self.set_result(cached_result)

        self.is_running = True
        self.result = None

        result = await fun(**kwargs)
        self.set_result(result)
