"""Inicializacion de la aplicacion Flask (factory)."""

from __future__ import annotations

from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.auth.routes import auth_bp
from app.web.routes import web_bp


def create_app() -> Flask:
    """Crea y configura la aplicacion Flask."""
    load_dotenv()
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.config.from_object(Config)

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("FLASK_ENV") == "production")

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)

    from app.web.routes import generar_csrf, es_billetera_congelada

    @app.context_processor
    def inject_csrf_and_state():
        return {
            "csrf_token": generar_csrf(),
            "billetera_congelada": es_billetera_congelada()
        }

    return app
