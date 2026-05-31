"""Pruebas STDD para auditoria (RED)."""

from __future__ import annotations

import pytest

from app.core.audit import registrar_operacion_auditoria


def test_registrar_operacion_auditoria_stub():
    assert registrar_operacion_auditoria(1, "transferencia", "detalle") is True
