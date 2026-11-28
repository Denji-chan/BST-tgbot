"""Mijoz botni bloklasa yoki qayta ochsa, bazada belgilaymiz (rassilkada hisobga olinmaydi)."""

from aiogram import F, Router
from aiogram.filters import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.repositories import users

router = Router(name="users.chat_member")
router.my_chat_member.filter(F.chat.type == "private")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def bot_blocked(event: ChatMemberUpdated, session: AsyncSession) -> None:
    await users.set_blocked_by_telegram_id(session, event.from_user.id, True)
    await session.commit()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def bot_unblocked(event: ChatMemberUpdated, session: AsyncSession) -> None:
    await users.set_blocked_by_telegram_id(session, event.from_user.id, False)
    await session.commit()
