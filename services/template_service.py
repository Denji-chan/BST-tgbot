from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from services import templates
from utils.db_api.repositories import templates as repo
from utils.misc.i18n import Translator


async def get_text(session: AsyncSession, translator: Translator, key: str, lang: str) -> str:
    """Bazadagi tahrirlangan matn yoki locales'dagi standart matn."""
    custom = await repo.get_text(session, key, lang)
    return custom if custom is not None else translator.raw(lang, templates.default_key(key))


async def save_text(session: AsyncSession, key: str, lang: str, text: str, admin_id: int, now: datetime) -> None:
    templates.validate(key, text)
    await repo.set_text(session, key, lang, text, admin_id, now)
    await session.commit()
