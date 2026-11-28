from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import NotificationLog


async def was_sent(session: AsyncSession, kind: str, key: str) -> bool:
    stmt = select(NotificationLog.id).where(NotificationLog.kind == kind, NotificationLog.key == key)
    return await session.scalar(stmt) is not None


async def mark_sent(session: AsyncSession, kind: str, key: str, now: datetime) -> None:
    session.add(NotificationLog(kind=kind, key=key, sent_at=now))
    await session.flush()
