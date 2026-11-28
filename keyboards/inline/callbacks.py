"""Barcha inline tugmalarning callback ma'lumotlari bir joyda."""

from aiogram.filters.callback_data import CallbackData


class LanguageCb(CallbackData, prefix="lang"):
    code: str


class SettingsLanguageCb(CallbackData, prefix="setlang"):
    code: str


class RegistrationCb(CallbackData, prefix="reg"):
    action: str  # ok | restart


class PurchaseCb(CallbackData, prefix="buy"):
    action: str  # use | skip | confirm | cancel


class StatsCb(CallbackData, prefix="stats"):
    period: str  # today | d7 | d30 | all


class UsersPageCb(CallbackData, prefix="users"):
    page: int


class UsersExportCb(CallbackData, prefix="users_xls"):
    pass


class TextKeyCb(CallbackData, prefix="tkey"):
    key: str


class TextLangCb(CallbackData, prefix="tlang"):
    key: str
    code: str


class TextActionCb(CallbackData, prefix="tact"):
    action: str  # edit | reset | back
    key: str
    code: str


class BroadcastCb(CallbackData, prefix="bc"):
    action: str  # send | cancel


class SupportReplyCb(CallbackData, prefix="sup"):
    message_id: int


class AdminRemoveCb(CallbackData, prefix="adm_rm"):
    telegram_id: int


class AdminAddCb(CallbackData, prefix="adm_add"):
    pass
