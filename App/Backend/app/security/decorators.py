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
            # En los endpoints actuales no hay estado del sistema precargado; se valida firma e impuesto.
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


def _construir_detalles_auditoria(tipo_operacion: str, transaccion: dict) -> str:
    """Construye string de detalles según tipo de operación para auditoría."""
    import json
    
    if tipo_operacion == "SPLIT":
        moneda_id = transaccion.get("moneda_id", "N/A")
        monedas_salida = transaccion.get("monedas_salida", [])
        particiones = [m.get("valor", 0) for m in monedas_salida]
        valor_total = sum(particiones)
        estado = transaccion.get("estado", "N/A")
        return f"Moneda: {moneda_id} | Particiones: {particiones} (Total: {valor_total}) | Estado: {estado}"
    
    elif tipo_operacion in ("TRANSFER", "Transferencia"):
        monto = transaccion.get("monto", 0)
        destino = transaccion.get("destino", "N/A")
        impuesto = transaccion.get("impuesto", 0)
        return f"Monto: {monto} | Impuesto: {impuesto} | Destino: {destino[:20]}..."
    
    elif tipo_operacion == "Recompensa":
        monto_entrada = sum(m.get("valor", 0) for m in transaccion.get("monedas_entrada", []))
        impuesto = transaccion.get("impuesto", 0)
        return f"Monto: {monto_entrada} | Impuesto: {impuesto}"
    
    else:
        # Default: intentar serializar detalles relevantes
        try:
            resumen = {
                "tipo": tipo_operacion,
                "estado": transaccion.get("estado", "N/A"),
                "entrada": sum(m.get("valor", 0) for m in transaccion.get("monedas_entrada", [])),
                "salida": sum(m.get("valor", 0) for m in transaccion.get("monedas_salida", []))
            }
            return json.dumps(resumen, ensure_ascii=False)
        except Exception:
            return "operacion registrada"
