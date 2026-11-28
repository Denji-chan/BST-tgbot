"""So'rovlar chastotasini cheklash mantig'i. aiogram'ga bog'liq emas, shuning uchun alohida testlanadi."""

import time
from collections.abc import Callable
from enum import Enum

DEFAULT_RATE = 0.5  # soniya
DEFAULT_KEY = "default"
_CLEANUP_THRESHOLD = 10_000
_STALE_AFTER = 60.0  # soniya


class ThrottleResult(Enum):
    ALLOWED = "allowed"  # handler ishlaydi
    FIRST_BLOCK = "first_block"  # bloklandi, foydalanuvchini bir marta ogohlantiramiz
    BLOCKED = "blocked"  # bloklandi, jim


def rate_limit(limit: float, key: str | None = None) -> dict:
    """Handler flaglari: `@router.message(..., flags=rate_limit(2, "start"))`."""
    flags: dict = {"rate_limit": limit}
    if key:
        flags["throttling_key"] = key
    return flags


class RateLimiter:
    def __init__(
        self,
        default_limit: float = DEFAULT_RATE,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.default_limit = default_limit
        self._clock = clock
        self._last: dict[tuple[int, str], float] = {}
        self._warned: set[tuple[int, str]] = set()

    def check(self, user_id: int, key: str, limit: float | None = None) -> ThrottleResult:
        limit = self.default_limit if limit is None else limit
        now = self._clock()
        k = (user_id, key)
        last = self._last.get(k)

        if last is None or now - last >= limit:
            self._last[k] = now
            self._warned.discard(k)
            self._cleanup(now)
            return ThrottleResult.ALLOWED

        if k not in self._warned:
            self._warned.add(k)
            return ThrottleResult.FIRST_BLOCK
        return ThrottleResult.BLOCKED

    def _cleanup(self, now: float) -> None:
        if len(self._last) < _CLEANUP_THRESHOLD:
            return
        stale = [k for k, t in self._last.items() if now - t > _STALE_AFTER]
        for k in stale:
            self._last.pop(k, None)
            self._warned.discard(k)
