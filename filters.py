"""Admin va developer filtrlari."""
from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from database import db


class IsAdmin(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user is not None and db.is_admin(event.from_user.id)


class IsDeveloper(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user is not None and db.is_developer(event.from_user.id)
