from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import TIMEZONE
from keyboards.inline.admin_lists import stats_keyboard
from keyboards.inline.callbacks import StatsCb
from services.periods import PERIODS
from services.stats_service import get_stats
from utils.misc.formatting import money
from utils.misc.i18n import Translate, i18n

router = Router(name="admins.stats")


async def _stats_text(session: AsyncSession, t: Translate, period: str) -> str:
    stats = await get_stats(session, period, datetime.now(TIMEZONE), TIMEZONE)
    return t(
        "stats.text",
        period=t(f"stats.period_{period}"),
        customers_total=stats.customers_total,
        customers_new=stats.customers_new,
        purchases_count=stats.purchases_count,
        purchases_sum=money(stats.purchases_sum),
        given=money(stats.cashback_given),
        used=money(stats.cashback_used),
        expired=money(stats.cashback_expired),
    )


@router.message(F.text.in_(i18n.variants("btn.admin_stats")))
async def stats_start(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    await state.clear()
    period = "today"
    await message.answer(await _stats_text(session, t, period), reply_markup=stats_keyboard(t, period))


@router.callback_query(StatsCb.filter(F.period.in_(set(PERIODS))))
async def stats_period(call: CallbackQuery, callback_data: StatsCb, session: AsyncSession, t: Translate) -> None:
    text = await _stats_text(session, t, callback_data.period)
    try:
        await call.message.edit_text(text, reply_markup=stats_keyboard(t, callback_data.period))
    except TelegramBadRequest:
        pass  # matn o'zgarmagan (xuddi shu davr qayta bosilgan)
    await call.answer()
