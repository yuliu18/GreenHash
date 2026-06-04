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
            clave_privada = None
            
            from flask import has_app_context, session
            if has_app_context():
                clave_publica = transaccion.get("origen", "")
                if session.get("clave_privada"):
                    clave_privada = session["clave_privada"]
                elif session.get(f"priv_key_{clave_publica}"):
                    clave_privada = session[f"priv_key_{clave_publica}"]
                else:
                    from app.db import get_db_connection
                    try:
                        with get_db_connection() as connection:
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "SELECT clave_privada FROM wallets WHERE clave_publica = %s",
                                    (clave_publica,)
                                )
                                row = cursor.fetchone()
                                if row and row.get("clave_privada"):
                                    clave_privada = row["clave_privada"]
                    except Exception:
                        pass
                if not clave_privada:
                    raise icontract.ViolationError("No existe una clave privada para realizar la firma digital.")
            else:
                clave_privada = "clave_privada_stub"

            firma = firmar_transaccion(transaccion, clave_privada)
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
            
            estado_sistema = {"saldos": {}}
            from flask import has_app_context
            if has_app_context():
                from app.db import get_db_connection
                try:
                    with get_db_connection() as connection:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT clave_publica, saldo FROM wallets")
                            for row in cursor.fetchall():
                                estado_sistema["saldos"][row["clave_publica"]] = row["saldo"]
                except Exception:
                    pass

            if not validar_transaccion(transaccion, estado_sistema):
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
                tipo_operacion = transaccion.get("tipo", "")
                
                # Extraer detalles relevantes según el tipo de operación
                detalles = _construir_detalles_auditoria(tipo_operacion, transaccion)
                registrar_operacion_auditoria(usuario_id, tipo_operacion, detalles)
            return transaccion
        except icontract.ViolationError as exc:
            from flask import has_app_context
            if has_app_context():
                flash(f"Infraccion de contrato: {exc}", "danger")
            raise

    return wrapper


def _alias_clave(clave: str) -> str:
    """Genera un alias corto y no sensible de una clave pública para los logs."""
    import hashlib
    if not clave or not isinstance(clave, str):
        return "desconocido"
    return "PK-" + hashlib.sha256(clave.encode()).hexdigest()[:6].upper()


def _fmt_gc(centavos: int) -> str:
    """Formatea centavos a GC con 2 decimales."""
    return f"{centavos / 100:.2f} GC"


def _construir_detalles_auditoria(tipo_operacion: str, transaccion: dict) -> str:
    """Construye string de detalles legibles para auditoría, sin exponer claves PEM."""

    if tipo_operacion == "SPLIT":
        moneda_id = transaccion.get("moneda_id", "N/A")
        monedas_salida = transaccion.get("monedas_salida", [])
        n_partes = len(monedas_salida)
        valor_total = sum(m.get("valor", 0) for m in monedas_salida)
        estado = transaccion.get("estado", "N/A")
        return (f"Moneda {moneda_id} dividida en {n_partes} parte(s) | "
                f"Total: {_fmt_gc(valor_total)} | Estado: {estado}")

    elif tipo_operacion == "MERGE":
        monedas_entrada = transaccion.get("monedas_entrada", [])
        monedas_salida = transaccion.get("monedas_salida", [])
        n_fusionadas = len(monedas_entrada)
        valor_total = sum(m.get("valor", 0) for m in monedas_salida)
        estado = transaccion.get("estado", "N/A")
        return (f"{n_fusionadas} moneda(s) fusionadas | "
                f"Resultado: {_fmt_gc(valor_total)} | Estado: {estado}")

    elif tipo_operacion in ("TRANSFER", "Transferencia"):
        monedas_entrada = transaccion.get("monedas_entrada", [])
        monedas_salida = transaccion.get("monedas_salida", [])
        monto_bruto = sum(m.get("valor", 0) for m in monedas_entrada)
        monto_neto = sum(m.get("valor", 0) for m in monedas_salida)
        impuesto = transaccion.get("impuesto", 0)
        destino_alias = _alias_clave(transaccion.get("destino", ""))
        estado = transaccion.get("estado", "N/A")
        return (f"Enviado: {_fmt_gc(monto_bruto)} → Destino {destino_alias} | "
                f"Neto: {_fmt_gc(monto_neto)} | Impuesto: {_fmt_gc(impuesto)} | Estado: {estado}")

    elif tipo_operacion in ("RECOMPENSA", "Recompensa"):
        monedas_salida = transaccion.get("monedas_salida", [])
        neto = sum(m.get("valor", 0) for m in monedas_salida)
        impuesto = transaccion.get("impuesto", 0)
        estado = transaccion.get("estado", "N/A")
        return (f"Recompensa acreditada: {_fmt_gc(neto)} | "
                f"Impuesto retenido: {_fmt_gc(impuesto)} | Estado: {estado}")

    else:
        entrada = sum(m.get("valor", 0) for m in transaccion.get("monedas_entrada", []))
        salida = sum(m.get("valor", 0) for m in transaccion.get("monedas_salida", []))
        estado = transaccion.get("estado", "N/A")
        return f"Entrada: {_fmt_gc(entrada)} | Salida: {_fmt_gc(salida)} | Estado: {estado}"
