"""Operaciones de recompensas (catálogo y reclamos)."""

from __future__ import annotations

import icontract
from flask import has_app_context
from app.db import get_db_connection


@icontract.require(lambda cartera: isinstance(cartera, dict))
@icontract.require(lambda material: isinstance(material, str) and material.strip() != "")
@icontract.require(lambda catalogo: isinstance(catalogo, dict))
@icontract.ensure(lambda result: isinstance(result, dict))
def registrar_recompensa_reciclaje(cartera: dict, material: str, catalogo: dict) -> dict:
    """Registra una recompensa por reciclaje (Stub para el equipo)."""
    raise NotImplementedError("STDD: implementar en rama feature/recompensas")


@icontract.require(lambda material: isinstance(material, str) and material.strip() != "")
@icontract.require(lambda catalogo: isinstance(catalogo, dict))
@icontract.ensure(lambda result: isinstance(result, int))
def consultar_catalogo_recompensas(material: str, catalogo: dict) -> int:
    """Consulta el catalogo de recompensas en base de datos o en el diccionario local."""
    if has_app_context():
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT precio FROM catalogo_recompensas WHERE material = %s",
                        (material,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return int(row["precio"])
        except Exception:
            pass

    # Fallback local
    return int(catalogo.get(material, 0))


@icontract.require(lambda catalogo: isinstance(catalogo, dict))
@icontract.require(lambda material: isinstance(material, str) and material.strip() != "")
@icontract.require(lambda precio: isinstance(precio, int) and precio >= 0)
@icontract.ensure(lambda result: isinstance(result, dict))
def modificar_catalogo_recompensas(catalogo: dict, material: str, precio: int) -> dict:
    """Modifica el precio de un material en el catalogo de recompensas (DB + dict local)."""
    # Actualizacion local
    catalogo[material] = precio

    if has_app_context():
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # UPSERT para MariaDB
                    cursor.execute(
                        "INSERT INTO catalogo_recompensas (material, precio) VALUES (%s, %s) "
                        "ON DUPLICATE KEY UPDATE precio = %s",
                        (material, precio, precio)
                    )
                connection.commit()
        except Exception:
            pass

    return catalogo
