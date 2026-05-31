"""Ayudantes de base de datos MariaDB con SQL parametrizado."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import pymysql
from flask import current_app


@contextmanager
def get_db_connection() -> Generator[pymysql.connections.Connection, None, None]:
    """Entrega una conexion a MariaDB. El caller controla commit/rollback."""
    config = current_app.config
    connection = pymysql.connect(
        host=config.get("DB_HOST"),
        port=int(config.get("DB_PORT")),
        user=config.get("DB_USER"),
        password=config.get("DB_PASSWORD"),
        database=config.get("DB_NAME"),
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        yield connection
    finally:
        connection.close()


def init_schema(schema_path: str) -> None:
    """Inicializa el esquema ejecutando el SQL DDL."""
    with open(schema_path, "r", encoding="utf-8") as handle:
        ddl = handle.read()
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for statement in ddl.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
        connection.commit()
