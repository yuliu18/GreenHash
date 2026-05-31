"""Pruebas STDD para decoradores de seguridad (RED)."""

from __future__ import annotations

import pytest

import icontract

from app.security.decorators import auditar, firmar, validar


def test_orden_decoradores_firma_antes_validar():
    llamadas = []

    @auditar
    @validar
    @firmar
    def operacion():
        llamadas.append("build")
        return {"tipo": "TRANSFER", "origen": "o", "destino": "d", "estado": "PENDIENTE"}

    resultado = operacion()
    assert isinstance(resultado, dict)


def test_violation_error_propagado(app):
    @validar
    def operacion_invalida():
        raise icontract.ViolationError("error")

    with app.test_request_context():
        with pytest.raises(icontract.ViolationError):
            operacion_invalida()
