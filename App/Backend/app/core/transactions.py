"""Operaciones de transaccion (stubs y helpers)."""

from __future__ import annotations

import icontract

from app.core.contracts import (
    LIMITE_MONEDAS_POR_CARTERA,
    TASA_IMPUESTO,
    TASA_IMPUESTO_RECOMPENSA,
)
from app.core.crypto import verificar_firma


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
    """Operacion TRANSFER (Modelo: Receptor paga el impuesto)."""
    saldo = origen.get("saldo", 0)
    if saldo < monto:
        raise ValueError(f"Fondos insuficientes: saldo={saldo}, monto requerido={monto}")
 
    impuesto = calcular_impuestos_transferencia(monto)
    neto_transferencia = monto - impuesto
    
    return {
        "tipo": "TRANSFER",
        "origen": origen.get("clave_publica", ""),
        "destino": destino_clave_publica,
        "monto": monto,
        "impuesto": impuesto,
        "estado": "VALIDA",
        # Conservación de valor: entrada (monto total) = salida (neto) + impuesto
        "monedas_entrada": [{"valor": monto}],
        "monedas_salida": [{"valor": neto_transferencia}],
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
    clave_publica = transaccion.get("origen", "")
    if not clave_publica:
        return False

    # verificar_firma confia (devuelve True) en claves no PEM. Por seguridad,
    # exigimos que la clave sea PEM real (exclusivo prod) o que pertenezca al set
    # oficial de claves seed de la demo académica (comienza con 'PUB_KEY_STUB_').
    # Esto previene bypasses de firmas con claves arbitrarias inventadas por atacantes.
    if not isinstance(clave_publica, str) or not (clave_publica.startswith("-----BEGIN") or clave_publica.startswith("PUB_KEY_STUB_")):
        return False

    if not verificar_firma(transaccion, clave_publica):
        return False

    # Coercion defensiva: cualquier campo no numerico de la transaccion (no confiable)
    # debe provocar un rechazo controlado (False) en lugar de una excepcion.
    try:
        impuesto = int(transaccion.get("impuesto", 0))
        monedas_entrada = transaccion.get("monedas_entrada", [])
        monedas_salida = transaccion.get("monedas_salida", [])
        total_entrada = _suma_valor_monedas(monedas_entrada)
        total_salida = _suma_valor_monedas(monedas_salida)
    except (ValueError, TypeError):
        return False

    tipo = transaccion.get("tipo", "").lower()

    if tipo in ("transfer", "transferencia"):
        # Guarda de positividad: rechaza transferencias de monto nulo o negativo
        # (incluye montos sub-umbral cuyo impuesto se trunca a 0).
        if total_entrada <= 0:
            return False
        monto = total_entrada
        # Aritmetica entera para evitar desincronizacion por truncamiento de float.
        impuesto_esperado = monto * int(TASA_IMPUESTO * 100) // 100
        if impuesto != impuesto_esperado:
            return False
        if total_entrada != total_salida + impuesto:
            return False
    elif tipo == "recompensa":
        if total_entrada <= 0:
            return False
        # Aritmetica entera para evitar desincronizacion por truncamiento de float.
        impuesto_esperado = total_entrada * int(TASA_IMPUESTO_RECOMPENSA * 100) // 100
        if impuesto != impuesto_esperado:
            return False
        if total_entrada != total_salida + impuesto:
            return False
    else:
        return False

    saldos = estado_sistema.get("saldos", {}) if isinstance(estado_sistema, dict) else {}
    try:
        saldo_actual = int(saldos.get(clave_publica, total_entrada))
    except (ValueError, TypeError):
        return False
    if saldo_actual < total_entrada:
        return False

    return True


@icontract.require(lambda monto: monto >= 0)
@icontract.ensure(lambda result: isinstance(result, int))
def calcular_impuestos_transferencia(monto: int) -> int:
    """Calcula la comision o impuesto estatal (2%) retenido sobre el monto."""
    return int(monto * TASA_IMPUESTO)
