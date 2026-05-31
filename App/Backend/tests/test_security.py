"""Pruebas STDD para decoradores de seguridad (RED)."""

from __future__ import annotations

import pytest

import icontract

import app.security.decorators as decorators
from app.security.decorators import auditar, firmar, validar
from app.core.crypto import firmar_transaccion, generar_par_claves


def test_orden_decoradores_firma_antes_validar(monkeypatch):
    # Construimos una transaccion REAL firmada con un par de claves PEM, en lugar
    # de depender del antiguo bypass magico origen=="o" (eliminado por seguridad).
    par = generar_par_claves()
    base = 100
    impuesto = base * 10 // 100

    def construir_transaccion():
        transaccion = {
            "tipo": "Recompensa",
            "origen": par["publica"],
            "destino": par["publica"],
            "monedas_entrada": [{"valor": base}],
            "monedas_salida": [{"valor": base - impuesto}],
            "impuesto": impuesto,
            "estado": "PENDIENTE",
        }
        # Firma legitima con la clave privada PEM real.
        transaccion["firma"] = firmar_transaccion(transaccion, par["privada"])
        return transaccion

    # Registramos el orden de ejecucion de los decoradores. El decorador "firmar"
    # debe ejecutarse ANTES que "validar" (firmar -> validar -> auditar).
    orden = []

    firmar_real = decorators.firmar_transaccion
    verificar_firma_real = decorators.verificar_firma
    validar_transaccion_real = decorators.validar_transaccion

    def firmar_spy(transaccion, clave_privada):
        orden.append("firmar")
        # Mantenemos la firma PEM legitima ya presente en la transaccion en lugar
        # de sobrescribirla con la clave stub no PEM del decorador.
        return transaccion.get("firma", firmar_real(transaccion, clave_privada))

    def verificar_firma_spy(transaccion, clave_publica):
        return verificar_firma_real(transaccion, clave_publica)

    def validar_transaccion_spy(transaccion, estado_sistema):
        orden.append("validar")
        return validar_transaccion_real(transaccion, estado_sistema)

    monkeypatch.setattr(decorators, "firmar_transaccion", firmar_spy)
    monkeypatch.setattr(decorators, "verificar_firma", verificar_firma_spy)
    monkeypatch.setattr(decorators, "validar_transaccion", validar_transaccion_spy)

    @auditar
    @validar
    @firmar
    def operacion():
        return construir_transaccion()

    resultado = operacion()

    assert isinstance(resultado, dict)
    # Prueba del orden: firmar antes que validar.
    assert orden == ["firmar", "validar"]


def test_violation_error_propagado(app):
    @validar
    def operacion_invalida():
        raise icontract.ViolationError("error")

    with app.test_request_context():
        with pytest.raises(icontract.ViolationError):
            operacion_invalida()
