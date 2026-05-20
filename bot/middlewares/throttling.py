import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)

RATE_LIMIT = 1.5      # секунд между запросами
CLEANUP_INTERVAL = 300  # чистим кэш каждые 5 минут


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = RATE_LIMIT):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}
        self._last_cleanup = time.monotonic()

    def _cleanup(self, now: float):
        if now - self._last_cleanup < CLEANUP_INTERVAL:
            return
        cutoff = now - CLEANUP_INTERVAL
        before = len(self.users)
        self.users = {uid: t for uid, t in self.users.items() if t > cutoff}
        logger.debug(f"Throttle cache cleanup: {before} → {len(self.users)} users")
        self._last_cleanup = now

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        now = time.monotonic()

        self._cleanup(now)

        last_time = self.users.get(user_id, 0)
        if now - last_time < self.rate_limit:
            logger.warning(f"User {user_id} is sending messages too fast")
            await event.answer("⚠️ Не так быстро. Подожди немного.")
            return

        self.users[user_id] = now
        return await handler(event, data)
    