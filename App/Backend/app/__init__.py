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

    # WAF (Web Application Firewall) preventivo para SQLi y XSS (UML-S DSM 1 y 4)
    # Detecta de forma temprana payloads en request.form o request.args, registra el incidente de forma no sensible
    # y bloquea el ataque antes de llegar a la lógica del backend o base de datos.
    from flask import request, abort
    import re
    from app.core.audit import registrar_operacion_auditoria
    from app.auth.session import obtener_usuario_id

    SQLI_PATTERNS = [
        re.compile(r"'\s*(?:or|and)\s+", re.IGNORECASE),
        re.compile(r"or\s+\d+\s*=\s*\d+", re.IGNORECASE),
        re.compile(r"union\s+select", re.IGNORECASE),
        re.compile(r"/\*.*?\*/", re.IGNORECASE),
    ]
    XSS_PATTERNS = [
        re.compile(r"<script", re.IGNORECASE),
        re.compile(r"javascript\s*:", re.IGNORECASE),
        re.compile(r"onload\s*=", re.IGNORECASE),
        re.compile(r"onerror\s*=", re.IGNORECASE),
        re.compile(r"<iframe", re.IGNORECASE),
    ]

    @app.before_request
    def waf_security_filter():
        # Revisamos todos los campos del form y parámetros query
        sources = [request.form, request.args]
        for src in sources:
            for key, val in src.items():
                if not isinstance(val, str):
                    continue
                # 1. Comprobar inyección SQL
                for pattern in SQLI_PATTERNS:
                    if pattern.search(val):
                        # Registro de auditoría mitigado (sin revelar la entrada sensible completa,
                        # solo el tipo de campo y el inicio del vector truncado)
                        safe_val = val[:15] + "..." if len(val) > 15 else val
                        usr_id = obtener_usuario_id()
                        registrar_operacion_auditoria(
                            usr_id, 
                            "SQLi_ATTEMPT", 
                            f"Intento de inyección SQL mitigado en campo '{key}'. Valor parcial: '{safe_val}'"
                        )
                        abort(400, description="Petición bloqueada por reglas del WAF de GreenHash.")

                # 2. Comprobar XSS
                for pattern in XSS_PATTERNS:
                    if pattern.search(val):
                        safe_val = val[:15] + "..." if len(val) > 15 else val
                        usr_id = obtener_usuario_id()
                        registrar_operacion_auditoria(
                            usr_id, 
                            "XSS_ATTEMPT", 
                            f"Intento de scripting XSS mitigado en campo '{key}'. Valor parcial: '{safe_val}'"
                        )
                        abort(400, description="Petición bloqueada por reglas del WAF de GreenHash.")

    from app.web.routes import generar_csrf, es_billetera_congelada

    @app.context_processor
    def inject_csrf_and_state():
        return {
            "csrf_token": generar_csrf(),
            "billetera_congelada": es_billetera_congelada()
        }

    return app
