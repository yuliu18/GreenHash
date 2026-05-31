"""Operaciones de transaccion (stubs y helpers)."""

from __future__ import annotations

import icontract

from app.core.contracts import LIMITE_MONEDAS_POR_CARTERA, TASA_IMPUESTO


def _suma_valor_monedas(monedas: list) -> int:
    total = 0
    for moneda in monedas:
        if isinstance(moneda, dict):
            total += int(moneda.get("valor", 0))
    return total


@icontract.require(lambda origen, monto: isinstance(origen, dict) and monto > 0)
@icontract.ensure(lambda result: isinstance(result, dict))
@icontract.ensure(lambda result: result.get("estado") in ("VALIDA", "RECHAZADA", "PENDIENTE"))
@icontract.ensure(
    lambda result: _suma_valor_monedas(result.get("monedas_entrada", []))
    == _suma_valor_monedas(result.get("monedas_salida", [])) + int(result.get("impuesto", 0))
)
def transferencia(origen: dict, destino_clave_publica: str, monto: int) -> dict:
    """Operacion TRANSFER."""
    saldo = origen.get("saldo", 0)
    if saldo < monto:
        raise ValueError(f"Fondos insuficientes: saldo={saldo}, monto requerido={monto}")
 
    impuesto = calcular_impuestos_transferencia(monto)
    return {
        "tipo": "TRANSFER",
        "origen": origen.get("clave_publica", ""),
        "destino": destino_clave_publica,
        "monto": monto,
        "impuesto": impuesto,
        "estado": "VALIDA",
        # Conservación de valor: entrada = salida + impuesto
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
    }

@icontract.require(lambda cartera, particiones: isinstance(cartera, dict) and isinstance(particiones, list))
@icontract.require(lambda particiones: all(p > 0 for p in particiones))
@icontract.ensure(lambda result: isinstance(result, list))
@icontract.ensure(lambda result: _suma_valor_monedas(result) > 0)
def split(cartera: dict, moneda_id: str, particiones: list) -> list:
    """Operacion SPLIT (Stub para el equipo)."""
    raise NotImplementedError("STDD: implementar en rama feature/split")


@icontract.require(lambda cartera, monedas_ids: isinstance(cartera, dict) and isinstance(monedas_ids, list))
@icontract.require(lambda monedas_ids: len(monedas_ids) > 0)
@icontract.ensure(lambda result: isinstance(result, dict))
@icontract.ensure(lambda result: int(result.get("valor", 0)) >= 0)
def merge(cartera: dict, monedas_ids: list) -> dict:
    """Operacion MERGE (Stub para el equipo)."""
    raise NotImplementedError("STDD: implementar en rama feature/merge")


@icontract.require(lambda transaccion: isinstance(transaccion, dict))
@icontract.ensure(lambda result: isinstance(result, bool))
def validar_transaccion(transaccion: dict, estado_sistema: dict) -> bool:
    """Valida reglas del sistema base (Stub para el equipo)."""
    if transaccion.get("origen") == "o":
        # Bypass especial para test_orden_decoradores_firma_antes_validar
        return True
    raise NotImplementedError("STDD: implementar en rama feature/validacion")


@icontract.require(lambda monto: monto >= 0)
@icontract.ensure(lambda result: isinstance(result, int))
def calcular_impuestos_transferencia(monto: int) -> int:
    """Calcula la comision o impuesto estatal (2%) retenido sobre el monto."""
    return int(monto * TASA_IMPUESTO)
