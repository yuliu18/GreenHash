"""Sesion en cookie segura (Flask session)."""

from __future__ import annotations

from flask import session


def iniciar_sesion(usuario_id: int, rol: str) -> None:
    """Guarda datos basicos de sesion en cookie segura."""
    session["usuario_id"] = usuario_id
    session["rol"] = rol


def cerrar_sesion() -> None:
    """Limpia la sesion actual."""
    session.clear()


def obtener_usuario_id() -> int | None:
    """Obtiene el id de usuario autenticado."""
    return session.get("usuario_id")


def obtener_rol() -> str | None:
    """Obtiene el rol actual."""
    return session.get("rol")
