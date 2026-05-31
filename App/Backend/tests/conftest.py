"""Fixtures base para pruebas STDD."""

from __future__ import annotations

import os
import sys

import pytest

# Backend/ es el root del paquete app
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
