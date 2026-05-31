"""Constantes y contratos comunes del dominio."""

from __future__ import annotations

import icontract

LIMITE_MONEDAS_POR_CARTERA = 100
TASA_IMPUESTO = 0.02


def cartera_valida(cartera: dict) -> bool:
    return isinstance(cartera, dict) and "saldo" in cartera


@icontract.require(lambda cartera: cartera_valida(cartera), "Cartera invalida")
def verificar_invariante_cartera(cartera: dict) -> bool:
    saldo = cartera.get("saldo", 0)
    return 0 <= saldo <= LIMITE_MONEDAS_POR_CARTERA
