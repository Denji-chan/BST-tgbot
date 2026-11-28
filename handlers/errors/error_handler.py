"""aiogram 3 uslubidagi umumiy xato handleri.

aiogram 2 dagi `@dp.errors_handler()` o'rniga `router.errors()` va `ErrorEvent`.
"""

import logging

from aiogram import Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import ErrorEvent

router = Router(name="errors.handler")
logger = logging.getLogger(__name__)


@router.errors()
async def errors_handler(event: ErrorEvent) -> bool:
    exc = event.exception
    update_id = event.update.update_id

    if isinstance(exc, TelegramForbiddenError):
        # Foydalanuvchi botni bloklagan. 15-taskda bazada belgilanadi.
        logger.info("Update %s: foydalanuvchi botni bloklagan", update_id)
        return True
    if isinstance(exc, TelegramRetryAfter):
        logger.warning("Update %s: Telegram limiti, %s soniya kutish kerak", update_id, exc.retry_after)
        return True
    if isinstance(exc, TelegramBadRequest):
        logger.warning("Update %s: TelegramBadRequest: %s", update_id, exc)
        return True

    logger.exception("Update %s: kutilmagan xato", update_id, exc_info=exc)
    return True
