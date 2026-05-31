"""Helpers de autenticacion: hashing y tokens."""

from __future__ import annotations

import secrets

import bcrypt


def hash_password(plain_password: str) -> str:
    """Genera hash bcrypt con salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password contra hash bcrypt."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_session_token() -> str:
    """Token de sesion opaco."""
    return secrets.token_urlsafe(32)
