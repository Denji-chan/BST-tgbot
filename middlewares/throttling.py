"""Spamdan himoya, aiogram 3 uslubida.

aiogram 2 dagi `@rate_limit` dekoratori o'rniga handler flaglari ishlatiladi:
    @router.message(Command("help"), flags=rate_limit(5, "help"))
Flag bo'lmasa, standart chegara qo'llanadi.
Hisob-kitob `utils.misc.throttling.RateLimiter` ichida, bu yerda faqat aiogram qismi.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

from utils.misc.throttling import DEFAULT_KEY, DEFAULT_RATE, RateLimiter, ThrottleResult


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limiter: RateLimiter | None = None) -> None:
        self.limiter = limiter or RateLimiter(default_limit=DEFAULT_RATE)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        limit = get_flag(data, "rate_limit")
        key = get_flag(data, "throttling_key") or DEFAULT_KEY
        result = self.limiter.check(user.id, key, limit)

        if result is ThrottleResult.ALLOWED:
            return await handler(event, data)

        if result is ThrottleResult.FIRST_BLOCK:
            t = data.get("t")
            warning = t("throttling.warning") if t else "..."
            if isinstance(event, Message):
                await event.answer(warning)
            elif isinstance(event, CallbackQuery):
                await event.answer(warning, show_alert=False)
        # Qayta-qayta yuborilganda jim e'tiborsiz qoldiramiz.
        return None
