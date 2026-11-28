"""Mijozlar ro'yxati (sahifalab) va Excel eksport."""

from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import TIMEZONE
from keyboards.inline.admin_lists import users_page_keyboard
from keyboards.inline.callbacks import UsersExportCb, UsersPageCb
from services.excel import CustomerRow, build_users_workbook
from services.periods import clamp_page, total_pages
from utils.db_api.repositories import users
from utils.misc.formatting import esc, fmt_date, local_date, money
from utils.misc.i18n import Translate, i18n

router = Router(name="admins.users_list")
PER_PAGE = 10


async def _page(session: AsyncSession, t: Translate, page: int) -> tuple[str, int, int]:
    total = await users.count_registered(session)
    page = clamp_page(page, total, PER_PAGE)
    pages = total_pages(total, PER_PAGE)
    if total == 0:
        return t("users.empty"), page, pages
    rows = await users.list_page(session, datetime.now(TIMEZONE), page * PER_PAGE, PER_PAGE)
    lines = []
    for row in rows:
        u = row.user
        last = fmt_date(local_date(u.last_purchase_at, TIMEZONE)) if u.last_purchase_at else t("users.never")
        lines.append(
            t(
                "users.line",
                customer_id=u.id,
                name=esc(u.full_name),
                phone=u.phone,
                balance=money(row.balance),
                purchases=money(row.purchases_sum),
                count=row.purchases_count,
                last=last,
                blocked=t("users.blocked_mark") if u.is_blocked else "",
            )
        )
    header = t("users.title", page=page + 1, pages=pages, total=total)
    return header + "\n\n" + "\n\n".join(lines), page, pages


@router.message(F.text.in_(i18n.variants("btn.admin_users")))
async def users_start(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    await state.clear()
    text, page, pages = await _page(session, t, 0)
    await message.answer(text, reply_markup=users_page_keyboard(t, page, pages))


@router.callback_query(UsersPageCb.filter())
async def users_page(call: CallbackQuery, callback_data: UsersPageCb, session: AsyncSession, t: Translate) -> None:
    text, page, pages = await _page(session, t, callback_data.page)
    try:
        await call.message.edit_text(text, reply_markup=users_page_keyboard(t, page, pages))
    except TelegramBadRequest:
        pass
    await call.answer()


@router.callback_query(UsersExportCb.filter())
async def users_export(call: CallbackQuery, session: AsyncSession, t: Translate) -> None:
    await call.answer(t("users.export_started"))
    now = datetime.now(TIMEZONE)
    rows = [
        CustomerRow(
            id=r.user.id,
            first_name=r.user.first_name,
            last_name=r.user.last_name,
            phone=r.user.phone,
            birth_date=r.user.birth_date,
            language=r.user.language,
            balance=r.balance,
            purchases_count=r.purchases_count,
            purchases_sum=r.purchases_sum,
            last_purchase_at=r.user.last_purchase_at,
            registered_at=r.user.registered_at,
            is_blocked=r.user.is_blocked,
        )
        for r in await users.list_all(session, now)
    ]
    content = build_users_workbook(rows, t, TIMEZONE)
    filename = f"mijozlar_{now.strftime('%Y-%m-%d_%H-%M')}.xlsx"
    await call.message.answer_document(
        BufferedInputFile(content, filename=filename), caption=t("users.export_caption", total=len(rows))
    )
