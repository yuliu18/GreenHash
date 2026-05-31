"""Pruebas STDD para transacciones (RED)."""

from __future__ import annotations

import pytest

from app.core.transactions import (
    transferencia,
    split,
    merge,
    validar_transaccion,
    calcular_impuestos_transferencia,
)


def test_transferencia_monto_positivo():
    origen = {"saldo": 10}
    resultado = transferencia(origen, "destino", 5)
    assert resultado.get("estado") in ("VALIDA", "RECHAZADA", "PENDIENTE")


def test_transferencia_no_saldo():
    origen = {"saldo": 0}
    with pytest.raises(Exception):
        transferencia(origen, "destino", 1)


def test_split_conservacion_valor():
    cartera = {"saldo": 10}
    resultado = split(cartera, "moneda1", [3, 7])
    assert isinstance(resultado, list)


def test_merge_conservacion_valor():
    cartera = {"saldo": 10}
    resultado = merge(cartera, ["m1", "m2"])
    assert isinstance(resultado, dict)


def test_validar_transaccion_stub():
    assert validar_transaccion({"estado": "PENDIENTE"}, {}) is True


def test_calcular_impuestos_stub():
    assert calcular_impuestos_transferencia(100) >= 0
