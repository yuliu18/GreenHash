"""Rutas de autenticacion (registro/login)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

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
                cursor.execute(
                    "INSERT INTO wallets (usuario_id, clave_publica, saldo, estado) VALUES (%s, %s, 0, 'ACTIVA')",
                    (user_id, pub_key)
                )
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
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not email or not password:
        flash("Credenciales incompletas", "warning")
        return redirect(url_for("auth.login_form"))

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password_hash, rol FROM usuarios WHERE email = %s", (email,))
            row = cursor.fetchone()

    if not row or not verify_password(password, row["password_hash"]):
        flash("Credenciales invalidas", "danger")
        return redirect(url_for("auth.login_form"))

    iniciar_sesion(row["id"], row["rol"])
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
