"""/start va ro'yxatdan o'tish: til -> ism -> familiya -> kontakt -> tug'ilgan kun -> tasdiqlash."""

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID, TIMEZONE
from keyboards.default.contact import contact_keyboard
from keyboards.default.main_menu import admin_menu, user_menu
from keyboards.inline.callbacks import LanguageCb, RegistrationCb
from keyboards.inline.language import language_keyboard
from keyboards.inline.registration import confirm_registration_keyboard
from services import referral
from services.registration_service import RegistrationStatus, register_user
from services.validators import clean_name, parse_birth_date
from states.registration import Registration
from utils.db_api.models import Admin, User
from utils.misc.formatting import esc, fmt_date
from utils.misc.i18n import LANGUAGES, Translate, Translator
from utils.misc.phone import normalize_phone
from utils.misc.throttling import rate_limit

router = Router(name="users.start")


@router.message(CommandStart(), flags=rate_limit(2, "start"))
async def bot_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    t: Translate,
    i18n: Translator,
    user: User | None,
    admin: Admin | None,
) -> None:
    await state.clear()
    if admin is not None:
        is_dev = message.from_user.id == DEVELOPER_ID
        await message.answer(t("admin.menu"), reply_markup=admin_menu(t, is_dev))
        return
    if user is not None:
        await message.answer(t("menu.welcome_back", name=esc(user.first_name)), reply_markup=user_menu(t))
        return

    await state.update_data(referrer_id=referral.parse_payload(command.args))
    await state.set_state(Registration.language)
    await message.answer(t("reg.choose_language"), reply_markup=language_keyboard(i18n))


@router.callback_query(Registration.language, LanguageCb.filter())
async def reg_language(call: CallbackQuery, callback_data: LanguageCb, state: FSMContext, i18n: Translator) -> None:
    code = callback_data.code if callback_data.code in LANGUAGES else i18n.default
    await state.update_data(lang=code)
    t = i18n.bind(code)
    await call.message.edit_text(t("reg.language_set"))
    await call.message.answer(t("reg.ask_first_name"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.first_name)
    await call.answer()


@router.message(Registration.first_name, F.text)
async def reg_first_name(message: Message, state: FSMContext, t: Translate) -> None:
    name = clean_name(message.text)
    if name is None:
        await message.answer(t("reg.bad_name"))
        return
    await state.update_data(first_name=name)
    await state.set_state(Registration.last_name)
    await message.answer(t("reg.ask_last_name"))


@router.message(Registration.last_name, F.text)
async def reg_last_name(message: Message, state: FSMContext, t: Translate) -> None:
    name = clean_name(message.text)
    if name is None:
        await message.answer(t("reg.bad_name"))
        return
    await state.update_data(last_name=name)
    await state.set_state(Registration.phone)
    await message.answer(t("reg.ask_phone"), reply_markup=contact_keyboard(t))


@router.message(Registration.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext, t: Translate) -> None:
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer(t("reg.not_your_contact"), reply_markup=contact_keyboard(t))
        return
    phone = normalize_phone(contact.phone_number)
    if phone is None:
        await message.answer(t("reg.bad_phone"), reply_markup=contact_keyboard(t))
        return
    await state.update_data(phone=phone)
    await state.set_state(Registration.birth_date)
    await message.answer(t("reg.ask_birth_date"), reply_markup=ReplyKeyboardRemove())


@router.message(Registration.phone)
async def reg_phone_wrong(message: Message, t: Translate) -> None:
    await message.answer(t("reg.press_contact_button"), reply_markup=contact_keyboard(t))


@router.message(Registration.birth_date, F.text)
async def reg_birth_date(message: Message, state: FSMContext, t: Translate) -> None:
    today = datetime.now(TIMEZONE).date()
    birth = parse_birth_date(message.text, today)
    if birth is None:
        await message.answer(t("reg.bad_birth_date"))
        return
    await state.update_data(birth_date=birth.isoformat())
    data = await state.get_data()
    await state.set_state(Registration.confirm)
    await message.answer(
        t(
            "reg.summary",
            first_name=esc(data["first_name"]),
            last_name=esc(data["last_name"]),
            phone=data["phone"],
            birth_date=fmt_date(birth),
        ),
        reply_markup=confirm_registration_keyboard(t),
    )


@router.message(Registration.first_name)
@router.message(Registration.last_name)
async def reg_name_not_text(message: Message, t: Translate) -> None:
    await message.answer(t("reg.bad_name"))


@router.message(Registration.birth_date)
async def reg_birth_not_text(message: Message, t: Translate) -> None:
    await message.answer(t("reg.bad_birth_date"))


@router.message(Registration.language)
@router.message(Registration.confirm)
async def reg_use_buttons(message: Message, t: Translate) -> None:
    await message.answer(t("common.use_buttons"))


@router.callback_query(Registration.confirm, RegistrationCb.filter(F.action == "restart"))
async def reg_restart(call: CallbackQuery, state: FSMContext, t: Translate) -> None:
    await state.set_state(Registration.first_name)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("reg.ask_first_name"))
    await call.answer()


@router.callback_query(Registration.confirm, RegistrationCb.filter(F.action == "ok"))
async def reg_confirm(call: CallbackQuery, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    data = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    result = await register_user(
        session,
        telegram_id=call.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        birth_date=datetime.fromisoformat(data["birth_date"]).date(),
        language=data.get("lang", t.lang),
        referrer_id=data.get("referrer_id"),
        now=datetime.now(TIMEZONE),
    )
    await state.clear()

    if result.status is RegistrationStatus.PHONE_TAKEN:
        await call.message.answer(t("reg.phone_taken"))
    elif result.status is RegistrationStatus.ALREADY_REGISTERED:
        await call.message.answer(t("reg.already_registered"), reply_markup=user_menu(t))
    else:
        await call.message.answer(
            t("reg.done", name=esc(result.user.first_name), customer_id=result.user.id),
            reply_markup=user_menu(t),
        )
        if result.referrer is not None:
            await call.message.answer(t("reg.referral_attached", name=esc(result.referrer.first_name)))
    await call.answer()
