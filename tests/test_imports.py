"""Barcha modullar xatosiz import bo'ladi va barcha routerlar ildiz routerga ulangan.

aiogram, sqlalchemy va boshqa paketlar o'rnatilgan muhitda ishlaydi (masalan, Docker yoki venv).
"""

import importlib
import os
import pkgutil
from pathlib import Path

import pytest

pytest.importorskip("aiogram")
pytest.importorskip("sqlalchemy")
pytest.importorskip("asyncpg")
pytest.importorskip("apscheduler")
pytest.importorskip("environs")

os.environ.setdefault("BOT_TOKEN", "123456789:AAH_test_token_abcdefghijklmnopqrstuv")
os.environ.setdefault("DEVELOPER_ID", "1")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["data", "filters", "handlers", "keyboards", "middlewares", "services", "states", "utils"]


def _all_modules():
    names = ["loader", "app"]
    for package in PACKAGES:
        names.append(package)
        for info in pkgutil.walk_packages([str(ROOT / package)], prefix=f"{package}."):
            names.append(info.name)
    return names


@pytest.mark.parametrize("name", _all_modules())
def test_module_imports(name):
    importlib.import_module(name)


def _collect(router, seen):
    seen.add(router.name)
    for sub in router.sub_routers:
        _collect(sub, seen)
    return seen


def test_all_routers_connected():
    import handlers

    root = handlers.setup_routers()
    names = _collect(root, set())
    expected = {
        "errors",
        "errors.handler",
        "groups",
        "channels",
        "admins",
        "admins.menu",
        "admins.purchase",
        "admins.support_reply",
        "admins.stats",
        "admins.users_list",
        "admins.texts",
        "admins.broadcast",
        "admins.admins",
        "users",
        "users.chat_member",
        "users.start",
        "users.help",
        "users.profile",
        "users.referral",
        "users.support",
        "users.settings",
        "fallback",
    }
    assert expected <= names, expected - names
