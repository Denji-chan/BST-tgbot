from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import MessageTemplate


async def get_text(session: AsyncSession, key: str, language: str) -> str | None:
    stmt = select(MessageTemplate.text).where(MessageTemplate.key == key, MessageTemplate.language == language)
    return await session.scalar(stmt)


async def set_text(session: AsyncSession, key: str, language: str, text: str, updated_by: int, now: datetime) -> None:
    template = await session.get(MessageTemplate, (key, language))
    if template is None:
        session.add(MessageTemplate(key=key, language=language, text=text, updated_by=updated_by, updated_at=now))
    else:
        template.text = text
        template.updated_by = updated_by
        template.updated_at = now
    await session.flush()
