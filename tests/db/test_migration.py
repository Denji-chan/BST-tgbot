"""Alembic migratsiyasi modellar bilan bir xil sxema yaratishini tekshiradi."""

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("alembic")
pytest.importorskip("aiosqlite")
pytest.importorskip("environs")

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine, inspect  # noqa: E402

from utils.db_api import models  # noqa: E402,F401
from utils.db_api.base import Base  # noqa: E402


def test_migration_matches_models(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    command.upgrade(Config("alembic.ini"), "head")

    inspector = inspect(create_engine(f"sqlite:///{db_file}"))
    migrated = set(inspector.get_table_names()) - {"alembic_version"}
    assert migrated == set(Base.metadata.tables)

    for name, table in Base.metadata.tables.items():
        columns = {c["name"] for c in inspector.get_columns(name)}
        assert columns == {c.name for c in table.columns}, name


def test_migration_downgrade(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    inspector = inspect(create_engine(f"sqlite:///{db_file}"))
    assert set(inspector.get_table_names()) == {"alembic_version"}
