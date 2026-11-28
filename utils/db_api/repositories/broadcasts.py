from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import Broadcast


async def create(
    session: AsyncSession,
    *,
    admin_telegram_id: int,
    content_type: str,
    source_chat_id: int,
    source_message_id: int,
    total: int,
    now: datetime,
) -> Broadcast:
    broadcast = Broadcast(
        admin_telegram_id=admin_telegram_id,
        content_type=content_type,
        source_chat_id=source_chat_id,
        source_message_id=source_message_id,
        total=total,
        delivered=0,
        failed=0,
        blocked=0,
        created_at=now,
    )
    session.add(broadcast)
    await session.flush()
    return broadcast


async def finish(
    session: AsyncSession, broadcast_id: int, *, delivered: int, failed: int, blocked: int, now: datetime
) -> None:
    broadcast = await session.get(Broadcast, broadcast_id)
    if broadcast is None:
        return
    broadcast.delivered = delivered
    broadcast.failed = failed
    broadcast.blocked = blocked
    broadcast.finished_at = now
    await session.flush()
