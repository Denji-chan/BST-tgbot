"""Barcha routerlarni bitta ildiz routerga yig'adi.

aiogram 2 dagi global `dp` va `@dp.message_handler` o'rniga har bir handler
faylida o'z `Router`i bor, ular shu yerda ulanadi.
Tartib muhim: errors -> guruh/kanal -> adminlar -> mijozlar -> fallback (eng oxirida).
"""

from aiogram import Router

from . import admins, channels, errors, groups, users
from .users import fallback


def setup_routers() -> Router:
    root = Router(name="root")
    root.include_routers(
        errors.router,
        groups.router,
        channels.router,
        admins.router,
        users.router,
        fallback.router,
    )
    return root
