"""Operaciones de cartera (stubs y helpers)."""

from __future__ import annotations

import icontract
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from app.core.contracts import LIMITE_MONEDAS_POR_CARTERA, cartera_valida


@icontract.require(lambda nombre_completo: isinstance(nombre_completo, str) and nombre_completo.strip() != "")
@icontract.ensure(lambda result: isinstance(result, dict))
def crear_cartera(nombre_completo: str) -> dict:
    """Crea una cartera con claves y saldo 0 (Stub para el equipo)."""
    
    # Primero lo que debo hacer es generar la clave privada usando curva elíptica (SECP256R1), usando la librería acordada e indicada y con eso genero la publica correspondiente que necesito para crear la cartera
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Segundo tengo que serializar clave privada a formato texto PEM como decidimos y dejamos especificado en el reparto de funciones
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    # Hago los mismo para serializar clave pública a formato texto PEM también para tener ambas en ese formato para la especificación y creacion de la cartera
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # Devuelvo el diccionario exacto que pide el contrato que sirve para la creación de la cartera al solicitarse
    return {
        "nombre_completo": nombre_completo,
        "clave_publica": public_pem,
        "clave_privada": private_pem,
        "saldo": 0
    }


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
    """Devuelve el saldo disponible en unidades enteras de GreenCoin."""
    return int(cartera.get("saldo", 0))
