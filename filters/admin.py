from aiogram.filters import Filter
from aiogram.types import TelegramObject

from data.config import DEVELOPER_ID
from utils.db_api.models import Admin


class IsAdmin(Filter):
    """Admin yoki Developer. `admin` LanguageMiddleware tomonidan bazadan yuklanadi."""

    async def __call__(self, event: TelegramObject, admin: Admin | None = None, **kwargs) -> bool:
        return admin is not None


class IsDeveloper(Filter):
    """Faqat .env dagi DEVELOPER_ID."""

    async def __call__(self, event: TelegramObject, event_from_user=None, **kwargs) -> bool:
        return event_from_user is not None and event_from_user.id == DEVELOPER_ID
