"""Rutas de autenticacion (registro/login)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for, session

from app.auth.helpers import hash_password, verify_password
from app.auth.session import iniciar_sesion, cerrar_sesion
from app.db import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/registro")
def registro_form():
    return render_template("registro.html")


@auth_bp.post("/registro")
def registrar_usuario():
    nombre = request.form.get("nombre_completo", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    
    # Por defecto, todos los que se registran desde la web son usuarios normales.
    # Los admins se deben asignar directamente en la BD o mediante otro mecanismo.
    rol = "usuario"

    if not nombre or not email or not password:
        flash("Datos incompletos para el registro", "warning")
        return redirect(url_for("auth.registro_form"))

    # 1. Verificar si el correo electrónico ya se encuentra registrado (Evita IntegrityError)
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("El correo electrónico ya está registrado. Intentá iniciar sesión o usá otro.", "danger")
                    return redirect(url_for("auth.registro_form"))
    except Exception as exc:
        flash(f"Error al verificar registros previos: {exc}", "danger")
        return redirect(url_for("auth.registro_form"))

    password_hash = hash_password(password)

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # 2. Insertar el nuevo usuario
                cursor.execute(
                    "INSERT INTO usuarios (nombre_completo, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
                    (nombre, email, password_hash, rol),
                )
                user_id = cursor.lastrowid
                
                # 3. Crear automáticamente su billetera con clave EC-SECP256R1 real
                from app.core.wallet import crear_cartera
                cartera = crear_cartera(nombre)
                pub_key = cartera["clave_publica"]
                priv_key = cartera["clave_privada"]
                cursor.execute(
                    "INSERT INTO wallets (usuario_id, clave_publica, clave_privada, saldo, estado) VALUES (%s, %s, %s, 0, 'ACTIVA')",
                    (user_id, pub_key, priv_key)
                )
                session[f"priv_key_{pub_key}"] = priv_key
                session["clave_privada"] = priv_key
            connection.commit()
    except Exception as exc:
        flash(f"Error de base de datos durante el registro: {exc}", "danger")
        return redirect(url_for("auth.registro_form"))

    flash("Registro exitoso, ahora podes iniciar sesion", "success")
    return redirect(url_for("auth.login_form"))


@auth_bp.get("/login")
def login_form():
    return render_template("login.html")


@auth_bp.post("/login")
def login_usuario():
    # Control de Fuerza Bruta / Credential Stuffing (UML-S DSM 1)
    from flask import request, session, flash, redirect, url_for
    import time
    from app.core.audit import registrar_operacion_auditoria

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not email or not password:
        flash("Credenciales incompletas", "warning")
        return redirect(url_for("auth.login_form"))

    ahora = time.time()
    intentos_session = session.get("login_attempts", {})
    # Limpiamos registros viejos de intentos (> 60 segundos)
    # Filtramos la lista de tiempos de intentos para cada clave
    intentos_session = {k: [t for t in v if ahora - t < 60] for k, v in intentos_session.items() if isinstance(v, list)}

    # Contamos intentos fallidos acumulados para este email o IP
    email_key = f"attempts_{email}"
    ip_key = f"attempts_{request.remote_addr}"

    intentos_email = len([t for t in intentos_session.get(email_key, [])])
    intentos_ip = len([t for t in intentos_session.get(ip_key, [])])

    if intentos_email >= 3 or intentos_ip >= 3:
        # Registramos el bloqueo mitigado en la auditoría sin credenciales
        registrar_operacion_auditoria(
            None,
            "BRUTE_FORCE_ATTEMPT",
            f"Fuerza bruta detectada en login para '{email[:12]}...'. Cuenta bloqueada temporalmente."
        )
        flash("⚠️ Demasiados intentos fallidos. Tu cuenta ha sido bloqueada temporalmente por seguridad (DSM 1).", "danger")
        return redirect(url_for("auth.login_form"))

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password_hash, rol FROM usuarios WHERE email = %s", (email,))
            row = cursor.fetchone()
            
            clave_privada = None
            if row:
                cursor.execute("SELECT clave_privada FROM wallets WHERE usuario_id = %s LIMIT 1", (row["id"],))
                w_row = cursor.fetchone()
                if w_row:
                    clave_privada = w_row.get("clave_privada")

    if not row or not verify_password(password, row["password_hash"]):
        # Registrar intento fallido
        if email_key not in intentos_session:
            intentos_session[email_key] = []
        if ip_key not in intentos_session:
            intentos_session[ip_key] = []
        intentos_session[email_key].append(ahora)
        intentos_session[ip_key].append(ahora)
        session["login_attempts"] = intentos_session

        flash("Credenciales invalidas", "danger")
        return redirect(url_for("auth.login_form"))

    # Resetear intentos si el login es exitoso
    if email_key in intentos_session:
        intentos_session.pop(email_key)
    if ip_key in intentos_session:
        intentos_session.pop(ip_key)
    session["login_attempts"] = intentos_session

    iniciar_sesion(row["id"], row["rol"])
    if clave_privada:
        session["clave_privada"] = clave_privada
    flash("Sesion iniciada", "success")
    return redirect(url_for("web.dashboard"))


@auth_bp.post("/logout")
def logout_usuario():
    from app.web.routes import _csrf_validar
    if not _csrf_validar():
        flash("Token CSRF inválido", "danger")
        return redirect(url_for("web.dashboard"))
    cerrar_sesion()
    flash("Sesion cerrada", "info")
    return redirect(url_for("web.index"))
