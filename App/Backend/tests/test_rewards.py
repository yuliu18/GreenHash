"""Pruebas STDD para recompensas (RED)."""

from __future__ import annotations

import pytest

from app.core.rewards import (
    registrar_recompensa_reciclaje,
    consultar_catalogo_recompensas,
    modificar_catalogo_recompensas,
)


def test_registrar_recompensa_stub():
    cartera = {"saldo": 0}
    resultado = registrar_recompensa_reciclaje(cartera, "plastico", {})
    assert isinstance(resultado, dict)


def test_consultar_catalogo_stub():
    assert consultar_catalogo_recompensas("plastico", {}) >= 0


def test_modificar_catalogo_stub():
    catalogo = modificar_catalogo_recompensas({}, "plastico", 10)
    assert catalogo.get("plastico") == 10
