"""Pruebas STDD para wallet (RED)."""

from __future__ import annotations

import pytest

from app.core.wallet import crear_cartera, eliminar_cartera, representacion_cartera, consultar_saldo


def test_crear_cartera_requiere_nombre():
    with pytest.raises(Exception):
        crear_cartera("")


def test_crear_cartera_no_implementado():
    cartera = crear_cartera("Usuario")
    assert cartera.get("saldo") == 0


def test_eliminar_cartera_saldo_cero():
    cartera = {"saldo": 0}
    assert eliminar_cartera(cartera) is True


def test_representacion_cartera_stub():
    cartera = {"saldo": 0}
    assert "saldo" in representacion_cartera(cartera)


def test_consultar_saldo_stub():
    cartera = {"saldo": 0}
    assert consultar_saldo(cartera) == 0
