"""SQLite bilan ishlash: mijozlar, adminlar, cashback amallari, sozlamalar."""
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from config import DB_PATH, DEFAULT_CASHBACK_PERCENT, DEVELOPER_ID, TZ


def now_str() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    # ------------------------------------------------------------------ setup
    def _create_tables(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,  -- mijoz raqami (ID)
                tg_id         INTEGER UNIQUE NOT NULL,
                username      TEXT,
                lang          TEXT,
                source        TEXT,
                phone         TEXT,
                full_name     TEXT,
                cashback      INTEGER NOT NULL DEFAULT 0,          -- so'mda
                is_registered INTEGER NOT NULL DEFAULT 0,
                is_blocked    INTEGER NOT NULL DEFAULT 0,
                created_at    TEXT NOT NULL,
                registered_at TEXT
            );

            CREATE TABLE IF NOT EXISTS admins (
                tg_id    INTEGER PRIMARY KEY,
                added_by INTEGER,
                added_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL REFERENCES users(id),
                admin_id        INTEGER NOT NULL,
                kind            TEXT NOT NULL CHECK (kind IN ('add', 'spend')),
                purchase_amount INTEGER NOT NULL DEFAULT 0,
                amount          INTEGER NOT NULL,
                percent         INTEGER,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
            CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id);
            """
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES ('cashback_percent', ?)",
            (str(DEFAULT_CASHBACK_PERCENT),),
        )
        self.conn.commit()

    def _exec(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def _one(self, sql: str, params: tuple = ()):
        return self.conn.execute(sql, params).fetchone()

    def _scalar(self, sql: str, params: tuple = ()):
        row = self._one(sql, params)
        return row[0] if row else None

    # ------------------------------------------------------------------ users
    def ensure_user(self, tg_id: int, username: Optional[str]) -> None:
        self._exec(
            "INSERT OR IGNORE INTO users(tg_id, username, created_at) VALUES (?, ?, ?)",
            (tg_id, username, now_str()),
        )
        self._exec("UPDATE users SET username = ?, is_blocked = 0 WHERE tg_id = ?", (username, tg_id))

    def get_user(self, tg_id: int) -> Optional[sqlite3.Row]:
        return self._one("SELECT * FROM users WHERE tg_id = ?", (tg_id,))

    def get_customer(self, user_id: int) -> Optional[sqlite3.Row]:
        return self._one("SELECT * FROM users WHERE id = ? AND is_registered = 1", (user_id,))

    def get_lang(self, tg_id: int) -> str:
        return self._scalar("SELECT lang FROM users WHERE tg_id = ?", (tg_id,)) or "uz"

    def has_lang(self, tg_id: int) -> bool:
        return self._scalar("SELECT lang FROM users WHERE tg_id = ?", (tg_id,)) is not None

    def set_lang(self, tg_id: int, lang: str) -> None:
        self._exec("UPDATE users SET lang = ? WHERE tg_id = ?", (lang, tg_id))

    def set_source(self, tg_id: int, source: str) -> None:
        self._exec("UPDATE users SET source = ? WHERE tg_id = ?", (source, tg_id))

    def set_phone(self, tg_id: int, phone: str) -> None:
        self._exec("UPDATE users SET phone = ? WHERE tg_id = ?", (phone, tg_id))

    def complete_registration(self, tg_id: int, full_name: str) -> None:
        self._exec(
            "UPDATE users SET full_name = ?, is_registered = 1, registered_at = ? WHERE tg_id = ?",
            (full_name, now_str(), tg_id),
        )

    def set_full_name(self, tg_id: int, full_name: str) -> None:
        self._exec("UPDATE users SET full_name = ? WHERE tg_id = ?", (full_name, tg_id))

    def mark_blocked(self, tg_id: int) -> None:
        self._exec("UPDATE users SET is_blocked = 1 WHERE tg_id = ?", (tg_id,))

    def active_customer_ids(self) -> list[int]:
        rows = self.conn.execute(
            "SELECT tg_id FROM users WHERE is_registered = 1 AND is_blocked = 0"
        ).fetchall()
        return [r[0] for r in rows]

    def find_customer(self, query: str) -> Optional[sqlite3.Row]:
        """Mijoz raqami (ID) yoki telefon raqami bo'yicha qidirish."""
        digits = re.sub(r"\D", "", query or "")
        if not digits:
            return None
        if len(digits) <= 7:  # qisqa son — mijoz ID
            return self.get_customer(int(digits))
        last9 = digits[-9:]
        return self._one(
            "SELECT * FROM users WHERE is_registered = 1 "
            "AND substr(replace(phone, '+', ''), -9) = ?",
            (last9,),
        )

    def all_customers(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM users WHERE is_registered = 1 ORDER BY id"
        ).fetchall()

    # --------------------------------------------------------------- cashback
    def get_percent(self) -> int:
        value = self._scalar("SELECT value FROM settings WHERE key = 'cashback_percent'")
        return int(value) if value is not None else DEFAULT_CASHBACK_PERCENT

    def set_percent(self, percent: int) -> None:
        self._exec(
            "INSERT INTO settings(key, value) VALUES ('cashback_percent', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(percent),),
        )

    def add_cashback(self, user_id: int, admin_id: int, purchase: int, amount: int, percent: int) -> int:
        """Cashback qo'shadi va yangi balansni qaytaradi."""
        with self.conn:
            self.conn.execute("UPDATE users SET cashback = cashback + ? WHERE id = ?", (amount, user_id))
            self.conn.execute(
                "INSERT INTO transactions(user_id, admin_id, kind, purchase_amount, amount, percent, created_at) "
                "VALUES (?, ?, 'add', ?, ?, ?, ?)",
                (user_id, admin_id, purchase, amount, percent, now_str()),
            )
        return self._scalar("SELECT cashback FROM users WHERE id = ?", (user_id,))

    def spend_cashback(self, user_id: int, admin_id: int, amount: int) -> Optional[int]:
        """Cashbackni ayiradi. Balans yetmasa None qaytaradi."""
        with self.conn:
            cur = self.conn.execute(
                "UPDATE users SET cashback = cashback - ? WHERE id = ? AND cashback >= ?",
                (amount, user_id, amount),
            )
            if cur.rowcount == 0:
                return None
            self.conn.execute(
                "INSERT INTO transactions(user_id, admin_id, kind, purchase_amount, amount, percent, created_at) "
                "VALUES (?, ?, 'spend', 0, ?, NULL, ?)",
                (user_id, admin_id, amount, now_str()),
            )
        return self._scalar("SELECT cashback FROM users WHERE id = ?", (user_id,))

    def history(self, user_id: int, limit: int = 10) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()

    def all_transactions(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT t.*, u.full_name, u.phone FROM transactions t "
            "JOIN users u ON u.id = t.user_id ORDER BY t.id"
        ).fetchall()

    # ----------------------------------------------------------------- admins
    def is_developer(self, tg_id: int) -> bool:
        return tg_id == DEVELOPER_ID

    def is_admin(self, tg_id: int) -> bool:
        if tg_id == DEVELOPER_ID:
            return True
        return self._one("SELECT 1 FROM admins WHERE tg_id = ?", (tg_id,)) is not None

    def add_admin(self, tg_id: int, added_by: int) -> bool:
        cur = self._exec(
            "INSERT OR IGNORE INTO admins(tg_id, added_by, added_at) VALUES (?, ?, ?)",
            (tg_id, added_by, now_str()),
        )
        return cur.rowcount > 0

    def remove_admin(self, tg_id: int) -> None:
        self._exec("DELETE FROM admins WHERE tg_id = ?", (tg_id,))

    def list_admins(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT a.tg_id, a.added_at, u.username, u.full_name FROM admins a "
            "LEFT JOIN users u ON u.tg_id = a.tg_id ORDER BY a.added_at"
        ).fetchall()

    # ------------------------------------------------------------- statistics
    def stats(self) -> dict:
        now = datetime.now(TZ)
        today = now.strftime("%Y-%m-%d 00:00:00")
        week = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        month = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        reg = "FROM users WHERE is_registered = 1"

        def count_since(since: str) -> int:
            return self._scalar(f"SELECT COUNT(*) {reg} AND registered_at >= ?", (since,))

        langs = self.conn.execute(
            f"SELECT COALESCE(lang, 'uz') AS k, COUNT(*) AS c {reg} GROUP BY k ORDER BY c DESC"
        ).fetchall()
        sources = self.conn.execute(
            f"SELECT COALESCE(source, 'other') AS k, COUNT(*) AS c {reg} GROUP BY k ORDER BY c DESC"
        ).fetchall()

        return {
            "total": self._scalar(f"SELECT COUNT(*) {reg}"),
            "today": count_since(today),
            "week": count_since(week),
            "month": count_since(month),
            "blocked": self._scalar(f"SELECT COUNT(*) {reg} AND is_blocked = 1"),
            "langs": [(r["k"], r["c"]) for r in langs],
            "sources": [(r["k"], r["c"]) for r in sources],
            "cb_balance": self._scalar(f"SELECT COALESCE(SUM(cashback), 0) {reg}"),
            "cb_given": self._scalar("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE kind = 'add'"),
            "cb_spent": self._scalar("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE kind = 'spend'"),
            "percent": self.get_percent(),
        }


db = Database(DB_PATH)
