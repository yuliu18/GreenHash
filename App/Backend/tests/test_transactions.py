"""Pruebas STDD para transacciones (RED)."""

from __future__ import annotations

import pytest

from app.core.crypto import firmar_transaccion, generar_par_claves
from app.core.contracts import TASA_IMPUESTO

from app.core.transactions import (
    transferencia,
    split,
    merge,
    validar_transaccion,
    calcular_impuestos_transferencia,
)


def test_transferencia_monto_positivo():
    origen = {"saldo": 10}
    with pytest.raises(NotImplementedError):
        transferencia(origen, "destino", 5)


def test_transferencia_no_saldo():
    origen = {"saldo": 0}
    with pytest.raises(NotImplementedError):
        transferencia(origen, "destino", 1)


def test_split_conservacion_valor():
    cartera = {"saldo": 10}
    with pytest.raises(NotImplementedError):
        split(cartera, "moneda1", [3, 7])


def test_merge_conservacion_valor():
    cartera = {"saldo": 10}
    with pytest.raises(NotImplementedError):
        merge(cartera, ["m1", "m2"])


@pytest.fixture(scope="module")
def par_claves():
    return generar_par_claves()


def _firmar(transaccion: dict, clave_privada: str) -> dict:
    firma = firmar_transaccion(transaccion, clave_privada)
    transaccion["firma"] = firma
    return transaccion


def test_validar_transaccion_transfer_valida(par_claves):
    origen = par_claves["publica"]
    monto = 100
    impuesto = int(monto * TASA_IMPUESTO)
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
        "impuesto": impuesto,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    estado_sistema = {"saldos": {origen: monto + impuesto}}
    assert validar_transaccion(transaccion, estado_sistema) is True


def test_validar_transaccion_transfer_firma_invalida(par_claves):
    origen = par_claves["publica"]
    monto = 50
    impuesto = int(monto * TASA_IMPUESTO)
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
        "impuesto": impuesto,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    transaccion["impuesto"] = impuesto + 1
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_transfer_impuesto_incorrecto(par_claves):
    origen = par_claves["publica"]
    monto = 80
    impuesto = int(monto * TASA_IMPUESTO)
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
        "impuesto": impuesto + 2,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_transfer_saldo_insuficiente(par_claves):
    origen = par_claves["publica"]
    monto = 60
    impuesto = int(monto * TASA_IMPUESTO)
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
        "impuesto": impuesto,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    estado_sistema = {"saldos": {origen: monto + impuesto - 1}}
    assert validar_transaccion(transaccion, estado_sistema) is False


def test_validar_transaccion_recompensa_valida(par_claves):
    origen = par_claves["publica"]
    base = 100
    impuesto = int(base * 0.10)
    transaccion = {
        "tipo": "Recompensa",
        "origen": origen,
        "destino": origen,
        "monedas_entrada": [{"valor": base}],
        "monedas_salida": [{"valor": base - impuesto}],
        "impuesto": impuesto,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    assert validar_transaccion(transaccion, {}) is True


def test_validar_transaccion_recompensa_impuesto_incorrecto(par_claves):
    origen = par_claves["publica"]
    base = 120
    impuesto = int(base * 0.10)
    transaccion = {
        "tipo": "Recompensa",
        "origen": origen,
        "destino": origen,
        "monedas_entrada": [{"valor": base}],
        "monedas_salida": [{"valor": base - impuesto}],
        "impuesto": impuesto + 1,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_origen_no_pem_rechazada():
    # FIX-2: un origen no PEM con una firma bogus debe ser rechazado, porque
    # verificar_firma confia en claves no PEM (devolveria True) y abriria un bypass.
    transaccion = {
        "tipo": "TRANSFER",
        "origen": "clave_falsa_no_pem",
        "destino": "destino",
        "monedas_entrada": [{"valor": 102}],
        "monedas_salida": [{"valor": 100}],
        "impuesto": 2,
        "firma": "firma_bogus",
        "estado": "PENDIENTE",
    }
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_firma_manipulada_rechazada(par_claves):
    # Aisla el fallo de firma: la transaccion es coherente en impuesto/conservacion,
    # pero solo la firma esta manipulada, por lo que debe rechazarse.
    origen = par_claves["publica"]
    monto = 100
    impuesto = int(monto * TASA_IMPUESTO)
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": monto + impuesto}],
        "monedas_salida": [{"valor": monto}],
        "impuesto": impuesto,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    # Solo se altera la firma; el resto de la transaccion sigue siendo valido.
    transaccion["firma"] = "00" + transaccion["firma"][2:]
    estado_sistema = {"saldos": {origen: monto + impuesto}}
    assert validar_transaccion(transaccion, estado_sistema) is False


def test_validar_transaccion_transfer_valor_cero_rechazada(par_claves):
    # FIX-4: una transferencia de valor cero debe rechazarse (guarda de positividad).
    origen = par_claves["publica"]
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": 0}],
        "monedas_salida": [{"valor": 0}],
        "impuesto": 0,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_impuesto_malformado_rechazada(par_claves):
    # FIX-3: un campo impuesto malformado ("abc") debe devolver False en lugar de
    # propagar ValueError/TypeError.
    origen = par_claves["publica"]
    transaccion = {
        "tipo": "TRANSFER",
        "origen": origen,
        "destino": "destino",
        "monedas_entrada": [{"valor": 102}],
        "monedas_salida": [{"valor": 100}],
        "impuesto": "abc",
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    assert validar_transaccion(transaccion, {}) is False


def test_calcular_impuestos_stub():
    assert calcular_impuestos_transferencia(100) >= 0
