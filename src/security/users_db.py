"""
FloraGuard — Kullanıcı Deposu
SQLite `users` tablosu; şifreler bcrypt ile hash'lenmiş olarak saklanır.
İlk çalıştırmada demo kullanıcılar (her rol için bir tane) otomatik seed edilir
— böylece RBAC uçtan uca hemen test edilebilir. Üretimde `seed_demo_users`
kaldırılmalı ve gerçek bir kayıt/onay akışı eklenmelidir.
"""

from __future__ import annotations

from pathlib import Path

from passlib.context import CryptContext

from src.data.database import get_connection
from src.data.schemas import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT
);
"""

_DEMO_USERS = [
    ("ciftci1", "ciftci123", Role.FARMER, "Demo Çiftçi"),
    ("danisman1", "danisman123", Role.ADVISOR, "Demo Danışman"),
    ("admin1", "admin123", Role.ADMIN, "Demo Admin"),
]


def init_users_table(db_path: Path) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(_SCHEMA)


def seed_demo_users(db_path: Path) -> None:
    """Yalnızca kullanıcı tablosu boşsa demo kullanıcıları ekler (idempotent)."""
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count > 0:
            return
        for username, password, role, full_name in _DEMO_USERS:
            conn.execute(
                "INSERT INTO users (username, hashed_password, role, full_name) VALUES (?, ?, ?, ?)",
                (username, pwd_context.hash(password), role.value, full_name),
            )


def get_user(db_path: Path, username: str) -> dict | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT username, hashed_password, role, full_name FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None


def get_user_role(db_path: Path, username: str) -> Role | None:
    """Kayıt sahibinin rolünü döner; kullanıcı sistemde kayıtlı değilse None
    (RBAC katmanı bunu Role.FARMER gibi ele alır — bkz. src/security/rbac.py)."""
    user = get_user(db_path, username)
    return Role(user["role"]) if user else None


def create_user(db_path: Path, username: str, password: str, role: Role, full_name: str = "") -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO users (username, hashed_password, role, full_name) VALUES (?, ?, ?, ?)",
            (username, pwd_context.hash(password), role.value, full_name),
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
