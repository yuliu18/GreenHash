"""Operaciones de cartera (stubs y helpers)."""

from __future__ import annotations

import icontract

from app.core.contracts import LIMITE_MONEDAS_POR_CARTERA, cartera_valida


@icontract.require(lambda nombre_completo: isinstance(nombre_completo, str) and nombre_completo.strip() != "")
@icontract.ensure(lambda result: isinstance(result, dict))
def crear_cartera(nombre_completo: str) -> dict:
    """Crea una cartera con claves y saldo 0 (Stub para el equipo)."""
    raise NotImplementedError("STDD: implementar en rama feature/wallet")


@icontract.require(lambda cartera: cartera_valida(cartera))
@icontract.require(lambda cartera: cartera.get("saldo", 0) == 0, "Saldo debe ser 0")
@icontract.ensure(lambda result: isinstance(result, bool))
def eliminar_cartera(cartera: dict) -> bool:
    """Elimina la cartera si no tiene saldo."""
    # 1. Validar saldo
    if cartera.get("saldo", 0) > 0:
        raise ValueError("Violación de seguridad: No se pueden destruir fondos activos.")
        
    # 2. Dar de baja criptográficamente la clave pública
    if "clave_publica" in cartera:
        cartera["clave_publica"] = "REVOCADA"
    
    if "clave_privada" in cartera:
        cartera["clave_privada"] = "REVOCADA"
        
    cartera["activa"] = False
    
    # 3. Devolvemos True indicando el éxito de la operación
    return True


@icontract.require(lambda cartera: cartera_valida(cartera))
@icontract.ensure(lambda result: isinstance(result, str))
def representacion_cartera(cartera: dict) -> str:
    """Devuelve una representacion legible de la cartera."""
    saldo = cartera.get("saldo", 0)
    usuario = cartera.get("nombre_completo", "Usuario")
    return f"Cartera de {usuario} | saldo: {saldo} GC"


@icontract.require(lambda cartera: cartera_valida(cartera))
@icontract.ensure(lambda result: isinstance(result, int))
@icontract.ensure(lambda result: 0 <= result <= LIMITE_MONEDAS_POR_CARTERA)
def consultar_saldo(cartera: dict) -> int:
    """Devuelve el saldo disponible (Stub para el equipo)."""
    raise NotImplementedError("STDD: implementar en rama feature/wallet")
