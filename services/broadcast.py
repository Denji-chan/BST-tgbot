"""Rassilka yadrosi: tezlik chegarasi, RetryAfter'ni kutish va hisobot. aiogram'ga bog'liq emas."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum

DEFAULT_RATE = 25  # xabar/soniya (Telegram umumiy chegarasi taxminan 30)
DEFAULT_MAX_RETRIES = 3


class DeliveryStatus(Enum):
    DELIVERED = "delivered"
    BLOCKED = "blocked"
    FAILED = "failed"


class RetryAfter(Exception):
    """Telegram "biroz kuting" dedi: `seconds` soniyadan keyin qayta urinish kerak."""

    def __init__(self, seconds: float) -> None:
        super().__init__(seconds)
        self.seconds = seconds


@dataclass
class BroadcastReport:
    total: int
    delivered: int = 0
    blocked: int = 0
    failed: int = 0
    blocked_user_ids: list[int] = field(default_factory=list)


async def run_broadcast(
    recipients: list[tuple[int, int]],
    send: Callable[[int], Awaitable[DeliveryStatus]],
    rate_per_second: float = DEFAULT_RATE,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> BroadcastReport:
    """`recipients`: [(user_id, chat_id), ...]. Har bir xabardan keyin 1/rate soniya kutiladi."""
    report = BroadcastReport(total=len(recipients))
    interval = 1 / rate_per_second
    for user_id, chat_id in recipients:
        retries = 0
        while True:
            try:
                status = await send(chat_id)
                break
            except RetryAfter as err:
                retries += 1
                if retries > max_retries:
                    status = DeliveryStatus.FAILED
                    break
                await sleep(err.seconds)
        if status is DeliveryStatus.DELIVERED:
            report.delivered += 1
        elif status is DeliveryStatus.BLOCKED:
            report.blocked += 1
            report.blocked_user_ids.append(user_id)
        else:
            report.failed += 1
        await sleep(interval)
    return report
