from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services import reengagement
from utils.db_api.models import User
from utils.db_api.repositories import notifications, users

NOTIFICATION_KIND = "reengagement"


@dataclass(frozen=True)
class DueMessage:
    user: User
    stage: int
    key: str


async def collect_due(session: AsyncSession, today: date, tz: ZoneInfo, stages: tuple[int, ...]) -> list[DueMessage]:
    """Bugun xabar yuborilishi kerak bo'lgan mijozlar (hech xarid qilmaganlar kirmaydi)."""
    result: list[DueMessage] = []
    for user in await users.active_users(session):
        if user.last_purchase_at is None:
            continue
        stage = reengagement.due_stage(user.last_purchase_at.astimezone(tz).date(), today, stages)
        if stage is None:
            continue
        key = reengagement.notification_key(user.id, stage, user.last_purchase_at)
        if await notifications.was_sent(session, NOTIFICATION_KIND, key):
            continue
        result.append(DueMessage(user=user, stage=stage, key=key))
    return result
