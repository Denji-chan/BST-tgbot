"""Matnlar bo'limi: 60/90/120 kunlik xabarlar va 25-sana eslatmasini 3 tilda tahrirlash."""

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID, TIMEZONE
from filters.menu import NOT_ADMIN_MENU
from keyboards.default.main_menu import admin_menu, cancel_keyboard
from keyboards.inline.callbacks import TextActionCb, TextKeyCb, TextLangCb
from keyboards.inline.texts import template_actions_keyboard, template_keys_keyboard, template_languages_keyboard
from services import template_service
from services.templates import TEMPLATE_FIELDS, TemplateError
from states.edit_text import EditText
from utils.misc.formatting import esc
from utils.misc.i18n import LANGUAGES, Translate, Translator, i18n

router = Router(name="admins.texts")


def _fields_hint(key: str) -> str:
    return ", ".join("{" + name + "}" for name in sorted(TEMPLATE_FIELDS[key]))


@router.message(F.text.in_(i18n.variants("btn.admin_texts")))
async def texts_start(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await message.answer(t("texts.choose"), reply_markup=template_keys_keyboard(t))


@router.callback_query(TextActionCb.filter(F.action == "back"))
async def texts_back(call: CallbackQuery, t: Translate) -> None:
    await call.message.edit_text(t("texts.choose"), reply_markup=template_keys_keyboard(t))
    await call.answer()


@router.callback_query(TextKeyCb.filter(F.key.in_(set(TEMPLATE_FIELDS))))
async def texts_key(call: CallbackQuery, callback_data: TextKeyCb, t: Translate, i18n: Translator) -> None:
    key = callback_data.key
    await call.message.edit_text(
        t("texts.choose_language", name=t(f"texts.name_{key}")),
        reply_markup=template_languages_keyboard(t, i18n, key),
    )
    await call.answer()


@router.callback_query(TextLangCb.filter(F.key.in_(set(TEMPLATE_FIELDS)) & F.code.in_(set(LANGUAGES))))
async def texts_show(
    call: CallbackQuery, callback_data: TextLangCb, session: AsyncSession, t: Translate, i18n: Translator
) -> None:
    key, code = callback_data.key, callback_data.code
    current = await template_service.get_text(session, i18n, key, code)
    await call.message.edit_text(
        t(
            "texts.current",
            name=t(f"texts.name_{key}"),
            language=i18n.get(code, "lang.name"),
            text=esc(current),
            fields=_fields_hint(key),
        ),
        reply_markup=template_actions_keyboard(t, key, code),
    )
    await call.answer()


@router.callback_query(TextActionCb.filter(F.action == "edit"))
async def texts_edit(call: CallbackQuery, callback_data: TextActionCb, state: FSMContext, t: Translate) -> None:
    if callback_data.key not in TEMPLATE_FIELDS or callback_data.code not in LANGUAGES:
        await call.answer(t("common.expired"))
        return
    await state.set_state(EditText.waiting_text)
    await state.update_data(template_key=callback_data.key, template_lang=callback_data.code)
    await call.message.answer(
        t("texts.send_new", fields=_fields_hint(callback_data.key)), reply_markup=cancel_keyboard(t)
    )
    await call.answer()


@router.message(EditText.waiting_text, F.text, NOT_ADMIN_MENU)
async def texts_save(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    data = await state.get_data()
    key, code = data["template_key"], data["template_lang"]
    try:
        await template_service.save_text(session, key, code, message.text, message.from_user.id, datetime.now(TIMEZONE))
    except TemplateError as err:
        if err.reason == "unknown_fields":
            await message.answer(t("texts.unknown_fields", unknown=", ".join(err.fields), fields=_fields_hint(key)))
        elif err.reason == "too_long":
            await message.answer(t("texts.too_long"))
        else:
            await message.answer(t("texts.bad_format"))
        return
    await state.clear()
    await message.answer(
        t("texts.saved", name=t(f"texts.name_{key}")),
        reply_markup=admin_menu(t, message.from_user.id == DEVELOPER_ID),
    )


@router.message(EditText.waiting_text, NOT_ADMIN_MENU)
async def texts_need_text(message: Message, t: Translate) -> None:
    await message.answer(t("purchase.need_text"))
