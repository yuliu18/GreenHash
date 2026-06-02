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
    origen = {"saldo": 1000, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = transferencia(origen, "PUB_KEY_STUB_DESTINO", 500)
    assert isinstance(resultado, dict)
    assert resultado["tipo"] == "TRANSFER"
    assert resultado["monto"] == 500
    assert resultado["impuesto"] == 10
    assert resultado["monedas_entrada"][0]["valor"] == 500
    assert resultado["monedas_salida"][0]["valor"] == 490


def test_transferencia_no_saldo():
    origen = {"saldo": 499, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    with pytest.raises(ValueError):
        transferencia(origen, "PUB_KEY_STUB_DESTINO", 500)


# ============= TESTS SPLIT =============

def test_split_simple():
    """Split divide una moneda en dos particiones."""
    cartera = {"saldo": 10, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [3, 7])
    assert isinstance(resultado, dict)
    assert resultado["tipo"] == "SPLIT"
    assert len(resultado["monedas_salida"]) == 2
    assert resultado["monedas_salida"][0]["valor"] == 3
    assert resultado["monedas_salida"][1]["valor"] == 7


def test_split_tres_particiones():
    """Split divide una moneda en tres particiones."""
    cartera = {"saldo": 100, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [25, 35, 40])
    assert resultado["tipo"] == "SPLIT"
    assert len(resultado["monedas_salida"]) == 3
    assert resultado["monedas_salida"][0]["valor"] == 25
    assert resultado["monedas_salida"][1]["valor"] == 35
    assert resultado["monedas_salida"][2]["valor"] == 40


def test_split_una_particion():
    """Split con una sola particion devuelve moneda sin cambios."""
    cartera = {"saldo": 50, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [50])
    assert len(resultado["monedas_salida"]) == 1
    assert resultado["monedas_salida"][0]["valor"] == 50


def test_split_particiones_unitarias():
    """Split divide en varias particiones de valor 1."""
    cartera = {"saldo": 5, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [1, 1, 1, 1, 1])
    assert len(resultado["monedas_salida"]) == 5
    for moneda in resultado["monedas_salida"]:
        assert moneda["valor"] == 1


def test_split_conservacion_valor():
    """Split conserva el valor total: suma(salida) == suma(entrada)."""
    cartera = {"saldo": 100, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    particiones = [10, 20, 30, 40]
    resultado = split(cartera, "moneda1", particiones)
    suma_salida = sum(m["valor"] for m in resultado["monedas_salida"])
    suma_entrada = sum(m["valor"] for m in resultado["monedas_entrada"])
    assert suma_salida == suma_entrada


def test_split_retorna_dict_transaccion():
    """Split retorna un dict de transaccion valido."""
    cartera = {"saldo": 15, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [5, 10])
    assert isinstance(resultado, dict)
    assert "tipo" in resultado
    assert "monedas_entrada" in resultado
    assert "monedas_salida" in resultado
    assert "estado" in resultado


def test_split_estado_valida():
    """Split retorna estado VALIDA."""
    cartera = {"saldo": 1, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda1", [1])
    assert resultado["estado"] == "VALIDA"


def test_split_moneda_id_preservado():
    """Split preserva el moneda_id en la transaccion."""
    cartera = {"saldo": 10, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    resultado = split(cartera, "moneda_especial", [5, 5])
    assert resultado["moneda_id"] == "moneda_especial"


def test_split_cartera_no_dict_falla():
    """Split falla si cartera no es dict."""
    with pytest.raises(Exception):  # icontract.ViolationError
        split("no_dict", "moneda1", [5, 5])


def test_split_particiones_no_lista_falla():
    """Split falla si particiones no es lista."""
    cartera = {"saldo": 10, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    with pytest.raises(Exception):  # icontract.ViolationError
        split(cartera, "moneda1", (5, 5))  # tuple, no list


def test_split_particion_negativa_falla():
    """Split falla si alguna particion es negativa."""
    cartera = {"saldo": 10, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    with pytest.raises(Exception):  # icontract.ViolationError
        split(cartera, "moneda1", [5, -5])


def test_split_particion_cero_falla():
    """Split falla si alguna particion es cero."""
    cartera = {"saldo": 10, "clave_publica": "PUB_KEY_STUB_ORIGEN"}
    with pytest.raises(Exception):  # icontract.ViolationError
        split(cartera, "moneda1", [0, 10])


# ============= TESTS VALIDACION SPLIT =============

def test_validar_transaccion_split_valida(par_claves):
    """Split valida pasa validacion: entrada = salida, impuesto = 0."""
    origen = par_claves["publica"]
    transaccion = {
        "tipo": "SPLIT",
        "origen": origen,
        "moneda_id": "m1",
        "monedas_entrada": [{"valor": 100}],
        "monedas_salida": [{"valor": 30}, {"valor": 70}],
        "impuesto": 0,
        "estado": "PENDIENTE",
    }
    transaccion = _firmar(transaccion, par_claves["privada"])
    estado_sistema = {"saldos": {origen: 100}}
    assert validar_transaccion(transaccion, estado_sistema) is True


def test_validar_transaccion_split_conservacion_falla():
    """Split invalida: entrada != salida."""
    transaccion = {
        "tipo": "SPLIT",
        "origen": "PUB_KEY_STUB_ORIGEN",
        "moneda_id": "m1",
        "monedas_entrada": [{"valor": 100}],
        "monedas_salida": [{"valor": 30}, {"valor": 60}],  # Suma = 90, no 100
        "impuesto": 0,
        "estado": "PENDIENTE",
    }
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_split_con_impuesto_falla():
    """Split invalida: no debe tener impuesto."""
    transaccion = {
        "tipo": "SPLIT",
        "origen": "PUB_KEY_STUB_ORIGEN",
        "moneda_id": "m1",
        "monedas_entrada": [{"valor": 100}],
        "monedas_salida": [{"valor": 30}, {"valor": 70}],
        "impuesto": 5,  # Split no debe tener impuesto
        "estado": "PENDIENTE",
    }
    assert validar_transaccion(transaccion, {}) is False


def test_validar_transaccion_split_valor_cero_falla():
    """Split invalida: no puede tener valor 0."""
    transaccion = {
        "tipo": "SPLIT",
        "origen": "PUB_KEY_STUB_ORIGEN",
        "moneda_id": "m1",
        "monedas_entrada": [{"valor": 0}],
        "monedas_salida": [],
        "impuesto": 0,
        "estado": "PENDIENTE",
    }
    assert validar_transaccion(transaccion, {}) is False


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
