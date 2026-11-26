"""Mijoz tomoni: ro'yxatdan o'tish, profil, cashback tarixi, sozlamalar."""
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from helpers import clean_name, history_text, normalize_phone, resume_registration, safe_edit
from keyboards import cancel_kb, lang_kb, menu_for, phone_kb, profile_kb, settings_kb, user_menu
from states import EditName, Reg
from texts import LANG_NAMES, LANGS, SOURCES, money, t, variants

router = Router(name="user")


# ================================================================ ro'yxatdan o'tish
@router.callback_query(F.data.startswith("reglang:"))
async def reg_lang(call: CallbackQuery, state: FSMContext) -> None:
    lang = call.data.split(":", 1)[1]
    if lang not in LANGS:
        await call.answer()
        return
    tg_id = call.from_user.id
    db.ensure_user(tg_id, call.from_user.username)
    db.set_lang(tg_id, lang)
    await call.answer()
    await safe_edit(call.message, f"✅ {LANG_NAMES[lang]}")
    user = db.get_user(tg_id)
    if not db.is_admin(tg_id) and not user["is_registered"]:
        await call.message.answer(t("welcome", lang))
    await resume_registration(call.message, state, tg_id)


@router.callback_query(F.data.startswith("src:"))
async def reg_source(call: CallbackQuery, state: FSMContext) -> None:
    key = call.data.split(":", 1)[1]
    user = db.get_user(call.from_user.id)
    if key not in SOURCES or user is None or user["is_registered"]:
        await call.answer()
        return
    lang = user["lang"] or "uz"
    db.set_source(call.from_user.id, key)
    await call.answer()
    await safe_edit(call.message, t("source_chosen", lang, source=t(f"src_{key}", lang)))
    await resume_registration(call.message, state, call.from_user.id)


@router.message(F.contact)
async def reg_contact(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    if user is None or not user["lang"] or user["is_registered"]:
        db.ensure_user(tg_id, message.from_user.username)
        await resume_registration(message, state, tg_id)
        return
    lang = user["lang"]
    if message.contact.user_id != tg_id:
        await message.answer(t("phone_not_own", lang), reply_markup=phone_kb(lang))
        return
    db.set_phone(tg_id, normalize_phone(message.contact.phone_number))
    await resume_registration(message, state, tg_id)


@router.message(Reg.phone)
async def reg_phone_not_contact(message: Message) -> None:
    lang = db.get_lang(message.from_user.id)
    await message.answer(t("phone_use_button", lang), reply_markup=phone_kb(lang))


@router.message(Reg.name, F.text)
async def reg_name(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    if user is None or user["is_registered"] or not user["phone"]:
        await resume_registration(message, state, tg_id)
        return
    lang = user["lang"] or "uz"
    name = clean_name(message.text)
    if name is None:
        await message.answer(t("name_invalid", lang))
        return
    db.complete_registration(tg_id, name)
    await state.clear()
    user = db.get_user(tg_id)
    await message.answer(
        t("reg_done", lang, name=escape(name), card=user["id"], percent=db.get_percent()),
        reply_markup=user_menu(lang),
    )


# ================================================================ profil
@router.message(F.text.in_(variants("btn_profile")))
async def profile(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    if user is None or not user["is_registered"]:
        await resume_registration(message, state, tg_id)
        return
    lang = user["lang"] or "uz"
    await message.answer(
        t(
            "profile", lang,
            card=user["id"],
            name=escape(user["full_name"]),
            phone=user["phone"],
            date=(user["registered_at"] or "")[:10],
            balance=money(user["cashback"], lang),
            percent=db.get_percent(),
        ),
        reply_markup=profile_kb(lang),
    )


@router.callback_query(F.data == "history")
async def history(call: CallbackQuery) -> None:
    user = db.get_user(call.from_user.id)
    await call.answer()
    if user is None or not user["is_registered"]:
        return
    await call.message.answer(history_text(user["id"], user["lang"] or "uz"))


# ================================================================ sozlamalar
@router.message(F.text.in_(variants("btn_settings")))
async def settings(message: Message, state: FSMContext) -> None:
    await state.clear()
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    if user is None or not user["lang"] or (not user["is_registered"] and not db.is_admin(tg_id)):
        await resume_registration(message, state, tg_id)
        return
    lang = user["lang"]
    await message.answer(
        t("settings", lang, lang=LANG_NAMES[lang]),
        reply_markup=settings_kb(lang, bool(user["is_registered"])),
    )


@router.callback_query(F.data == "set:lang")
async def settings_lang(call: CallbackQuery) -> None:
    await call.answer()
    await safe_edit(call.message, t("choose_lang"), reply_markup=lang_kb("chlang"))


@router.callback_query(F.data.startswith("chlang:"))
async def change_lang(call: CallbackQuery) -> None:
    lang = call.data.split(":", 1)[1]
    if lang not in LANGS:
        await call.answer()
        return
    tg_id = call.from_user.id
    db.set_lang(tg_id, lang)
    await call.answer()
    await safe_edit(call.message, f"✅ {LANG_NAMES[lang]}")
    await call.message.answer(t("lang_changed", lang), reply_markup=menu_for(tg_id, lang))


@router.callback_query(F.data == "set:name")
async def settings_name(call: CallbackQuery, state: FSMContext) -> None:
    user = db.get_user(call.from_user.id)
    await call.answer()
    if user is None or not user["is_registered"]:
        return
    lang = user["lang"] or "uz"
    await state.set_state(EditName.name)
    await call.message.answer(t("ask_name", lang), reply_markup=cancel_kb(lang))


@router.message(EditName.name, F.text)
async def edit_name(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    lang = db.get_lang(tg_id)
    name = clean_name(message.text)
    if name is None:
        await message.answer(t("name_invalid", lang))
        return
    db.set_full_name(tg_id, name)
    await state.clear()
    await message.answer(t("name_changed", lang), reply_markup=menu_for(tg_id, lang))


# ================================================================ boshqa xabarlar
@router.message()
async def fallback(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    if user is None or not user["lang"] or (not user["is_registered"] and not db.is_admin(tg_id)):
        db.ensure_user(tg_id, message.from_user.username)
        await resume_registration(message, state, tg_id)
        return
    lang = user["lang"]
    await message.answer(t("use_menu", lang), reply_markup=menu_for(tg_id, lang))


@router.callback_query()
async def fallback_callback(call: CallbackQuery) -> None:
    await call.answer()
