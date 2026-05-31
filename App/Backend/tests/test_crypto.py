"""Pruebas STDD para criptografia (RED)."""

from __future__ import annotations

import pytest

from app.core.crypto import firmar_transaccion, verificar_firma, generar_par_claves


def test_firmar_transaccion_stub():
    firma = firmar_transaccion({"tipo": "TRANSFER"}, "clave_privada")
    assert isinstance(firma, str)


def test_verificar_firma_stub():
    assert verificar_firma({"tipo": "TRANSFER"}, "clave_publica") is True


def test_generar_par_claves_stub():
    claves = generar_par_claves()
    assert "publica" in claves and "privada" in claves
