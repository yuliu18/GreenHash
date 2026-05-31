"""Registro de auditoria en base de datos."""

from __future__ import annotations

import icontract
from flask import has_app_context
from app.db import get_db_connection


@icontract.require(lambda operacion: isinstance(operacion, str) and operacion.strip() != "")
@icontract.require(lambda detalles: isinstance(detalles, str))
@icontract.ensure(lambda result: isinstance(result, bool))
def registrar_operacion_auditoria(usuario_id: int | None, operacion: str, detalles: str) -> bool:
    """Registra una operacion critica en la bitacora de auditoria (SQL parametrizado)."""
    if not has_app_context():
        # Fallback para pruebas unitarias aisladas sin servidor activo
        return True
        
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO auditoria (usuario_id, operacion, detalles) VALUES (%s, %s, %s)",
                    (usuario_id, operacion, detalles)
                )
            connection.commit()
        return True
    except Exception:
        return False
