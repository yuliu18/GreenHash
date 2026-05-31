"""Decoradores de seguridad para operaciones de valor."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

import icontract
from flask import abort, flash, redirect, url_for

from app.auth.session import obtener_rol, obtener_usuario_id
from app.core.audit import registrar_operacion_auditoria
from app.core.crypto import firmar_transaccion, verificar_firma
from app.core.transactions import validar_transaccion


def requiere_rol(rol_requerido: str) -> Callable:
    """Valida rol en sesion y aborta con 403 si no coincide."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            rol = obtener_rol()
            if rol is None:
                flash("Iniciá sesión para continuar", "warning")
                return redirect(url_for("auth.login_form"))
            if rol_requerido == "usuario" and rol not in ("usuario", "admin"):
                abort(403)
            elif rol_requerido != "usuario" and rol != rol_requerido:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def firmar(func: Callable) -> Callable:
    """build -> firmar: agrega firma digital a la transaccion."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            transaccion = func(*args, **kwargs)
            firma = firmar_transaccion(transaccion, "clave_privada_stub")
            transaccion["firma"] = firma
            return transaccion
        except icontract.ViolationError as exc:
            from flask import has_app_context
            if has_app_context():
                flash(f"Infraccion de contrato: {exc}", "danger")
            raise

    return wrapper


def validar(func: Callable) -> Callable:
    """firmar -> validar: valida reglas del sistema base."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            transaccion = func(*args, **kwargs)
            if not verificar_firma(transaccion, transaccion.get("origen", "")):
                raise icontract.ViolationError("Firma invalida")
            if not validar_transaccion(transaccion, {}):
                raise icontract.ViolationError("Validacion rechazada")
            return transaccion
        except icontract.ViolationError as exc:
            from flask import has_app_context
            if has_app_context():
                flash(f"Infraccion de contrato: {exc}", "danger")
            raise

    return wrapper


def auditar(func: Callable) -> Callable:
    """validar -> auditar: registra la operacion sin secretos."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            transaccion = func(*args, **kwargs)
            from flask import has_app_context
            if has_app_context():
                usuario_id = obtener_usuario_id()
                registrar_operacion_auditoria(usuario_id, transaccion.get("tipo", ""), "operacion registrada")
            return transaccion
        except icontract.ViolationError as exc:
            from flask import has_app_context
            if has_app_context():
                flash(f"Infraccion de contrato: {exc}", "danger")
            raise

    return wrapper
