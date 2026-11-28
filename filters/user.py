from aiogram.filters import Filter
from aiogram.types import TelegramObject

from utils.db_api.models import User


class IsRegistered(Filter):
    """Ro'yxatdan o'tgan mijoz. `user` LanguageMiddleware tomonidan yuklanadi."""

    async def __call__(self, event: TelegramObject, user: User | None = None, **kwargs) -> bool:
        return user is not None
