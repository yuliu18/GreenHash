"""Rutas web principales (shell)."""

from __future__ import annotations

import secrets
import json
import datetime
import uuid

import icontract
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.auth.session import obtener_usuario_id
from app.db import get_db_connection
from app.security.decorators import auditar, firmar, requiere_rol, validar
from app.core.transactions import transferencia, split, merge
from app.core.wallet import crear_cartera, eliminar_cartera, consultar_saldo
from app.core.rewards import consultar_catalogo_recompensas, modificar_catalogo_recompensas
from app.core.audit import registrar_operacion_auditoria

web_bp = Blueprint("web", __name__)


# Mapeo estático para conservar la interfaz gráfica premium del catálogo
PRODUCT_METADATA = {
    "Silla Algas": {
        "desc": "Hecho de plástico reciclado y residuos marinos en el campus.",
        "img": "products/silla.png",
    },
    "Mochila Eco": {
        "desc": "Tela reciclada resistente y diseño sobrio ideal para estudiantes.",
        "img": "products/mochila.png",
    },
    "Botella Verde": {
        "desc": "Botella reutilizable de aluminio reciclado ultraligero.",
        "img": "products/botella.png",
    },
    "Maceta Bio": {
        "desc": "Bioplástico biodegradable e inteligente para tus plantas.",
        "img": "products/maceta.png",
    },
}


def generar_csrf() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(24)
        session["csrf_token"] = token
    return token


def _csrf_validar() -> bool:
    token_form = request.form.get("csrf_token", "")
    token_session = session.get("csrf_token", "")
    return token_form and token_form == token_session


def es_billetera_congelada() -> bool:
    user_id = obtener_usuario_id()
    if not user_id:
        return False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT estado FROM wallets WHERE usuario_id = %s", (user_id,))
                row = cur.fetchone()
                if row and row["estado"] == "CONGELADA":
                    return True
    except Exception:
        pass
    return False


def get_current_user_and_balance() -> tuple[dict | None, float]:
    user_id = obtener_usuario_id()
    if not user_id:
        return None, 0.0
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT nombre_completo as nombreCompleto, email FROM usuarios WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()
            cur.execute("SELECT saldo FROM wallets WHERE usuario_id = %s", (user_id,))
            wallet = cur.fetchone()
            saldo = float(wallet["saldo"]) / 100.0 if wallet else 0.0
            return user, saldo


def get_current_user_wallet_details() -> tuple[dict | None, float, str]:
    user_id = obtener_usuario_id()
    if not user_id:
        return None, 0.0, ""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT nombre_completo as nombreCompleto, email FROM usuarios WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()
            cur.execute("SELECT saldo, clave_publica FROM wallets WHERE usuario_id = %s", (user_id,))
            wallet = cur.fetchone()
            saldo = float(wallet["saldo"]) / 100.0 if wallet else 0.0
            clave_publica = wallet["clave_publica"] if wallet else ""
            return user, saldo, clave_publica


@web_bp.get("/")
def index():
    from app.auth.session import obtener_rol

    if obtener_rol():
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("auth.login_form"))


@web_bp.get("/dashboard")
@requiere_rol("usuario")
def dashboard():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    transacciones = []
    
    if clave_publica:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp "
                        "FROM transacciones "
                        "WHERE origen = %s OR destino = %s "
                        "ORDER BY creado_en DESC LIMIT 4",
                        (clave_publica, clave_publica),
                    )
                    rows = cur.fetchall()
                    for r in rows:
                        is_sender = (r["origen"] == clave_publica)
                        try:
                            # Para recompensas se muestra el neto (monedas_salida).
                            # Para compras se muestra el costo (monedas_entrada).
                            # Para transferencias:
                            # - Si eres emisor (sender), tu costo es monedas_entrada (monto + impuesto).
                            # - Si eres receptor (receiver), tu ganancia neta es monedas_salida (monto).
                            tipo_upper = r["tipo"].upper()
                            if tipo_upper == "RECOMPENSA":
                                campo_monedas = "monedas_salida"
                            elif tipo_upper == "COMPRA":
                                campo_monedas = "monedas_entrada"
                            else: # TRANSFER
                                campo_monedas = "monedas_entrada" if is_sender else "monedas_salida"
                            
                            coins = json.loads(r[campo_monedas])
                            val = sum(float(c.get("valor", 0)) for c in coins) / 100.0
                        except Exception:
                            val = 0.0

                        if tipo_upper == "COMPRA":
                            desc = f"Canje: {r['destino']}"
                            amount = -val
                        elif tipo_upper == "RECOMPENSA":
                            desc = "Recompensa por reciclaje"
                            amount = val
                        else:
                            if is_sender:
                                desc = f"Enviado a {r['destino']}"
                                amount = -val
                            else:
                                desc = f"Recibido de {r['origen']}"
                                amount = val

                        transacciones.append({
                            "id": r["id"],
                            "date": r["timestamp"],
                            "type": r["tipo"],
                            "desc": desc,
                            "amount": amount
                        })
        except Exception:
            pass

    return render_template(
        "dashboard.html",
        saldo_actual=saldo_actual,
        transacciones=transacciones,
        current_user=current_user,
    )


@web_bp.get("/transferir")
@requiere_rol("usuario")
def transferir_form():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("transferir.html", current_user=current_user, saldo_actual=saldo_actual, tx_result=None)


@web_bp.post("/transferir")
@requiere_rol("usuario")
def transferir_accion():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.transferir_form"))

    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.transferir_form"))

    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    # Escalamos el saldo a centavos de GreenCoin para el dominio
    origen = {
        "clave_publica": clave_publica,
        "saldo": int(saldo_actual * 100),
        "nombre_completo": current_user["nombreCompleto"] if current_user else "Usuario"
    }
    # Normalizar la clave PEM: el textarea puede enviar \r\n (Windows) → normalizar a \n
    # No hacer strip() total para no quitar el \n final de las claves PEM almacenadas en BD
    destino_input = request.form.get("destino", "").replace("\r\n", "\n").replace("\r", "\n").strip()
    try:
        monto = int(float(request.form.get("monto", "0")) * 100)
    except (ValueError, TypeError):
        monto = 0

    # 1. Búsqueda inteligente del destinatario (por Clave Pública, Email o Nombre Completo)
    destino_clave_publica = ""
    destino_nombre = ""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Buscar por clave exacta, con o sin \n final, o por email/nombre
                destino_con_newline = destino_input if destino_input.endswith("\n") else destino_input + "\n"
                destino_sin_newline = destino_input.rstrip("\n")
                cur.execute(
                    "SELECT w.clave_publica, u.nombre_completo FROM wallets w "
                    "JOIN usuarios u ON w.usuario_id = u.id "
                    "WHERE w.clave_publica = %s OR w.clave_publica = %s OR w.clave_publica = %s "
                    "OR u.email = %s OR u.nombre_completo = %s",
                    (destino_input, destino_con_newline, destino_sin_newline, destino_input, destino_input)
                )
                row = cur.fetchone()
                if row:
                    destino_clave_publica = row["clave_publica"]
                    destino_nombre = row["nombre_completo"]
    except Exception:
        pass

    if not destino_clave_publica:
        flash("El destinatario no existe en la red GreenHash (ingresa su Nombre, Email o Clave Pública)", "danger")
        return redirect(url_for("web.transferir_form"))

    if destino_clave_publica == clave_publica:
        flash("No puedes transferir GreenCoins a tu propia billetera.", "danger")
        return redirect(url_for("web.transferir_form"))

    @auditar
    @validar
    @firmar
    def _operacion():
        return transferencia(origen, destino_clave_publica, monto)

    try:
        transaccion = _operacion()
        
        # 2. Persistencia atómica en Base de Datos MariaDB
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Debitar del emisor (monto bruto)
                costo_total = transaccion["monedas_entrada"][0]["valor"]
                cur.execute(
                    "UPDATE wallets SET saldo = saldo - %s WHERE clave_publica = %s",
                    (costo_total, transaccion["origen"])
                )
                # Acreditar al destinatario (monto neto con impuesto deducido)
                monto_transferencia = transaccion["monedas_salida"][0]["valor"]
                cur.execute(
                    "UPDATE wallets SET saldo = saldo + %s WHERE clave_publica = %s",
                    (monto_transferencia, transaccion["destino"])
                )
                # C3/W2: Envía la tasa de impuesto de transferencias (2%) a la cuenta de tesorería del sistema ('admin@greenhash.eco')
                impuesto = transaccion.get("impuesto", 0)
                if impuesto > 0:
                    cur.execute(
                        "SELECT w.clave_publica FROM wallets w "
                        "JOIN usuarios u ON w.usuario_id = u.id "
                        "WHERE u.email = %s",
                        ("admin@greenhash.eco",)
                    )
                    admin_row = cur.fetchone()
                    if admin_row:
                        cur.execute(
                            "UPDATE wallets SET saldo = saldo + %s WHERE clave_publica = %s",
                            (impuesto, admin_row["clave_publica"])
                        )
                # Registrar en el ledger inmutable
                import json
                import datetime
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    "INSERT INTO transacciones (tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        transaccion["tipo"].upper(),
                        transaccion["origen"],
                        transaccion["destino"],
                        json.dumps(transaccion["monedas_entrada"]),
                        json.dumps(transaccion["monedas_salida"]),
                        transaccion["impuesto"],
                        timestamp_str,
                        transaccion.get("firma", ""),
                        transaccion["estado"]
                    )
                )
            conn.commit()
            
        monto_bruto_display = float(costo_total) / 100.0
        monto_neto_display = float(monto_transferencia) / 100.0
        impuesto_display = float(transaccion["impuesto"]) / 100.0
        current_user, saldo_actual = get_current_user_and_balance()
        tx_result = {
            "estado": transaccion["estado"],
            "destino_nombre": destino_nombre,
            "destino_clave": destino_clave_publica[:28] + "...",
            "monto_enviado": monto_bruto_display,
            "monto_recibido": monto_neto_display,
            "impuesto": impuesto_display,
            "timestamp": timestamp_str,
        }
        return render_template("transferir.html", current_user=current_user, saldo_actual=saldo_actual, tx_result=tx_result)
    except NotImplementedError:
        flash("Funcionalidad no implementada todavia", "warning")
    except ValueError as exc:
        flash(f"Error de negocio: {exc}", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infracción de contrato: {exc}", "danger")
    return redirect(url_for("web.transferir_form"))


@web_bp.get("/split")
@requiere_rol("usuario")
def split_form():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("split.html", current_user=current_user, saldo_actual=saldo_actual)


@web_bp.post("/split")
@requiere_rol("usuario")
def split_accion():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.split_form"))

    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.billetera", tab="split"))

    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    cartera = {
        "clave_publica": clave_publica,
        "saldo": int(saldo_actual * 100),
        "nombre_completo": current_user["nombreCompleto"] if current_user else "Usuario"
    }
    moneda_id = request.form.get("moneda_id", "").strip()
    if not moneda_id:
        flash("El identificador de moneda no puede estar vacío.", "danger")
        return redirect(url_for("web.billetera", tab="split"))

    try:
        particiones = [int(p.strip()) for p in request.form.get("particiones", "").split(",") if p.strip()]
    except ValueError:
        flash("Las particiones deben ser números enteros positivos separados por comas (ej: 3, 5, 2).", "danger")
        return redirect(url_for("web.billetera", tab="split"))

    if not particiones:
        flash("Debes ingresar al menos una partición.", "danger")
        return redirect(url_for("web.billetera", tab="split"))

    @auditar
    @validar
    @firmar
    def _operacion():
        return split(cartera, moneda_id, particiones)

    try:
        transaccion = _operacion()

        # Persistencia en el ledger inmutable
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # C3: Descontar y acreditar para asegurar consistencia del saldo en centavos
                valor_entrada = sum(m["valor"] for m in transaccion["monedas_entrada"])
                valor_salida = sum(m["valor"] for m in transaccion["monedas_salida"])
                cur.execute(
                    "UPDATE wallets SET saldo = saldo - %s WHERE clave_publica = %s",
                    (valor_entrada, transaccion["origen"])
                )
                cur.execute(
                    "UPDATE wallets SET saldo = saldo + %s WHERE clave_publica = %s",
                    (valor_salida, transaccion["origen"])
                )
                
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    "INSERT INTO transacciones (tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        transaccion["tipo"].upper(),
                        transaccion.get("origen", clave_publica),
                        transaccion.get("moneda_id", moneda_id),
                        json.dumps(transaccion["monedas_entrada"]),
                        json.dumps(transaccion["monedas_salida"]),
                        transaccion.get("impuesto", 0),
                        timestamp_str,
                        transaccion.get("firma", ""),
                        transaccion["estado"],
                    ),
                )
            conn.commit()

        n_partes = len(transaccion["monedas_salida"])
        valor_total = sum(m["valor"] for m in transaccion["monedas_entrada"])
        flash(f"SPLIT ejecutado: moneda '{moneda_id}' dividida en {n_partes} partes (total {valor_total / 100:.2f} GC). Transacción registrada en el ledger.", "success")
    except NotImplementedError:
        flash("Funcionalidad no implementada todavia", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infraccion de contrato: {exc}", "danger")
    except Exception as exc:
        flash(f"Error al registrar el split: {exc}", "danger")
    return redirect(url_for("web.billetera", tab="split"))


@web_bp.get("/merge")
@requiere_rol("usuario")
def merge_form():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("merge.html", current_user=current_user, saldo_actual=saldo_actual)


@web_bp.post("/merge")
@requiere_rol("usuario")
def merge_accion():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.merge_form"))

    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.billetera", tab="merge"))

    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    cartera = {
        "clave_publica": clave_publica,
        "saldo": int(saldo_actual * 100),
        "nombre_completo": current_user["nombreCompleto"] if current_user else "Usuario"
    }

    monedas_ids = request.form.getlist("monedas_ids[]")
    valores_raw = request.form.getlist("valores[]")

    if len(monedas_ids) < 2:
        flash("Debes seleccionar al menos 2 monedas para fusionar.", "danger")
        return redirect(url_for("web.billetera", tab="merge"))

    try:
        valores = [int(v) for v in valores_raw]
    except (ValueError, TypeError):
        flash("Valores de monedas invalidos.", "danger")
        return redirect(url_for("web.billetera", tab="merge"))

    @auditar
    @validar
    @firmar
    def _operacion():
        return merge(cartera, monedas_ids, valores)

    try:
        transaccion = _operacion()

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # C3: Descontar y acreditar para asegurar consistencia del saldo en centavos
                valor_entrada = sum(m["valor"] for m in transaccion["monedas_entrada"])
                valor_salida = sum(m["valor"] for m in transaccion["monedas_salida"])
                cur.execute(
                    "UPDATE wallets SET saldo = saldo - %s WHERE clave_publica = %s",
                    (valor_entrada, transaccion["origen"])
                )
                cur.execute(
                    "UPDATE wallets SET saldo = saldo + %s WHERE clave_publica = %s",
                    (valor_salida, transaccion["origen"])
                )
                
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    "INSERT INTO transacciones (tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        transaccion["tipo"].upper(),
                        transaccion.get("origen", clave_publica),
                        transaccion.get("origen", clave_publica),
                        json.dumps(transaccion["monedas_entrada"]),
                        json.dumps(transaccion["monedas_salida"]),
                        transaccion.get("impuesto", 0),
                        timestamp_str,
                        transaccion.get("firma", ""),
                        transaccion["estado"],
                    ),
                )
            conn.commit()

        moneda_resultado = transaccion["monedas_salida"][0]
        flash(
            f"MERGE ejecutado: {len(monedas_ids)} monedas fusionadas en '{moneda_resultado['id']}' "
            f"(total {moneda_resultado['valor'] / 100:.2f} GC). Transacción registrada en el ledger.",
            "success"
        )
    except icontract.ViolationError as exc:
        flash(f"Infraccion de contrato: {exc}", "danger")
    except Exception as exc:
        flash(f"Error al registrar el merge: {exc}", "danger")

    return redirect(url_for("web.billetera", tab="merge"))


@web_bp.get("/tienda")
@requiere_rol("usuario")
def tienda():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    catalogo = []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Solo traemos los 4 productos fisicos canjeables de la tienda
                cur.execute(
                    "SELECT id, material as name, precio/100.0 as price FROM catalogo_recompensas "
                    "WHERE material IN ('Silla Algas', 'Mochila Eco', 'Botella Verde', 'Maceta Bio') "
                    "ORDER BY material"
                )
                rows = cur.fetchall()
                for r in rows:
                    name = r["name"]
                    metadata = PRODUCT_METADATA.get(name, {
                        "desc": "Producto ecológico certificado del campus.",
                        "img": "products/default.png"
                    })
                    catalogo.append({
                        "id": r["id"],
                        "name": name,
                        "price": float(r["price"]),
                        "desc": metadata["desc"],
                        "img": metadata["img"]
                    })
    except Exception:
        pass

    return render_template("tienda.html", catalogo=catalogo, current_user=current_user, saldo_actual=saldo_actual)


@web_bp.post("/tienda/comprar")
@requiere_rol("usuario")
def comprar_recompensa():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.tienda"))

    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.tienda"))
    
    producto_id = request.form.get("producto_id", "")
    user_id = obtener_usuario_id()
    
    if not producto_id or not user_id:
        flash("Datos de compra invalidos", "danger")
        return redirect(url_for("web.tienda"))
        
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Obtener detalles del producto
                cur.execute("SELECT material, precio FROM catalogo_recompensas WHERE id = %s", (producto_id,))
                producto = cur.fetchone()
                if not producto:
                    flash("El producto no existe en el catálogo", "danger")
                    return redirect(url_for("web.tienda"))
                
                material = producto["material"]
                precio = int(producto["precio"])
                
                # 2. Obtener saldo de cartera y llave pública
                cur.execute("SELECT id, saldo, clave_publica FROM wallets WHERE usuario_id = %s", (user_id,))
                wallet = cur.fetchone()
                if not wallet:
                    flash("No posees una billetera activa en el sistema", "danger")
                    return redirect(url_for("web.tienda"))
                    
                saldo_actual = wallet["saldo"]
                clave_publica = wallet["clave_publica"]
                
                if saldo_actual < precio:
                    flash(f"Saldo insuficiente ({saldo_actual / 100.0:.2f} GC) para canjear '{material}' ({precio / 100.0:.2f} GC)", "warning")
                    return redirect(url_for("web.tienda"))
                    
                # 3. Debitar balance
                nuevo_saldo = saldo_actual - precio
                cur.execute("UPDATE wallets SET saldo = %s WHERE usuario_id = %s", (nuevo_saldo, user_id))
                
                # 4. Insertar transacción
                timestamp_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                coins_json = json.dumps([{"valor": precio}])
                cur.execute(
                    "INSERT INTO transacciones (tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        "Compra",
                        clave_publica,
                        material,
                        coins_json,
                        coins_json,
                        0,
                        timestamp_str,
                        "COMPRA_AUTORIZADA_SISTEMA",
                        "VALIDA"
                    )
                )
                
                # 5. Registrar en la bitácora de auditoría
                registrar_operacion_auditoria(
                    user_id,
                    "Compra",
                    f"Canjeó recompensa '{material}' por {precio} GC (Saldo restante: {nuevo_saldo} GC)"
                )
                
            conn.commit()
            flash(f"¡Canje de '{material}' por {precio} GC realizado con éxito!", "success")
            
    except Exception as exc:
        flash(f"Error procesando el canje en base de datos: {exc}", "danger")
        
    return redirect(url_for("web.tienda"))


@web_bp.post("/tienda/consultar")
@requiere_rol("usuario")
def tienda_consultar():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.tienda"))
    material = request.form.get("material", "")
    try:
        consultar_catalogo_recompensas(material, {})
        flash("Consulta realizada", "success")
    except NotImplementedError:
        flash("Funcionalidad no implementada todavia", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infraccion de contrato: {exc}", "danger")
    return redirect(url_for("web.tienda"))


@web_bp.get("/beneficios")
@requiere_rol("usuario")
def beneficios():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    search_query = request.args.get("q", "").strip()
    materiales = []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if search_query:
                    # Inserción parametrizada para búsqueda segura contra inyecciones SQL (UML-S DSM 4)
                    cur.execute(
                        "SELECT material, precio/100.0 as precio FROM catalogo_recompensas "
                        "WHERE material LIKE %s AND material IN ('Plástico PET', 'Aluminio / Latas', 'Vidrio', 'Papel y Cartón') "
                        "ORDER BY material",
                        (f"%{search_query}%",)
                    )
                else:
                    cur.execute(
                        "SELECT material, precio/100.0 as precio FROM catalogo_recompensas "
                        "WHERE material IN ('Plástico PET', 'Aluminio / Latas', 'Vidrio', 'Papel y Cartón') "
                        "ORDER BY material"
                    )
                rows = cur.fetchall()
                for r in rows:
                    materiales.append({
                        "material": r["material"],
                        "precio": float(r["precio"])
                    })
    except Exception:
        pass

    return render_template(
        "beneficios.html",
        current_user=current_user,
        saldo_actual=saldo_actual,
        materiales=materiales,
        search_query=search_query
    )


@web_bp.get("/auditoria")
@requiere_rol("admin")
def auditoria():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    registros = []
    wallets_list = []
    catalogo_items = []
    
    # Pre-calcular marcas de tiempo para los registros de ataque simulados en el WAF (DSM 1)
    now = datetime.datetime.now()
    sqli_time = (now - datetime.timedelta(minutes=12)).strftime("%d/%m/%Y %H:%M")
    xss_time = (now - datetime.timedelta(minutes=35)).strftime("%d/%m/%Y %H:%M")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Obtener bitácora de auditoría real
                cur.execute(
                    "SELECT a.id, u.nombre_completo as usuario, a.operacion as accion, a.detalles as detalle, a.creado_en as fecha "
                    "FROM auditoria a LEFT JOIN usuarios u ON a.usuario_id = u.id "
                    "ORDER BY a.creado_en DESC"
                )
                rows = cur.fetchall()
                for r in rows:
                    date_str = r["fecha"].strftime("%d/%m/%Y %H:%M") if r["fecha"] else "N/A"
                    registros.append({
                        "id": r["id"],
                        "usuario": r["usuario"] if r["usuario"] else "Sistema/Invitado",
                        "accion": r["accion"],
                        "detalle": r["detalle"],
                        "fecha": date_str,
                        "estado": "OK"
                    })
                    
                # 2. Obtener billeteras reales
                cur.execute(
                    "SELECT u.nombre_completo as usuario, u.email, w.clave_publica, w.saldo, w.id as wallet_id "
                    "FROM usuarios u JOIN wallets w ON u.id = w.usuario_id WHERE u.rol = 'usuario' "
                    "ORDER BY u.nombre_completo"
                )
                wallet_rows = cur.fetchall()
                for wr in wallet_rows:
                    wallets_list.append({
                        "id": wr["wallet_id"],
                        "usuario": wr["usuario"],
                        "email": wr["email"],
                        "clave_publica": wr["clave_publica"],
                        "saldo": float(wr["saldo"])
                    })
                    
                # 3. Obtener catálogo real
                cur.execute("SELECT id, material, precio FROM catalogo_recompensas ORDER BY material")
                cat_rows = cur.fetchall()
                for cr in cat_rows:
                    catalogo_items.append({
                        "id": cr["id"],
                        "material": cr["material"],
                        "precio": float(cr["precio"])
                    })
    except Exception:
        pass

    return render_template(
        "auditoria.html",
        registros=registros,
        wallets=wallets_list,
        catalogo_items=catalogo_items,
        current_user=current_user,
        saldo_actual=saldo_actual,
        sqli_time=sqli_time,
        xss_time=xss_time
    )


@web_bp.post("/auditoria/agregar-producto")
@requiere_rol("admin")
def agregar_producto():
    from flask import jsonify
    if not _csrf_validar():
        return jsonify({"status": "danger", "message": "Token CSRF inválido"}), 400
        
    material = request.form.get("material", "").strip()
    precio_str = request.form.get("precio", "0").strip()
    
    if not material or not precio_str:
        return jsonify({"status": "danger", "message": "Campos requeridos vacíos"}), 400
        
    try:
        precio = int(float(precio_str))
        # Invocar la función segura ya implementada del núcleo
        modificar_catalogo_recompensas({}, material, precio)
        
        user_id = obtener_usuario_id()
        registrar_operacion_auditoria(
            user_id,
            "Gestión Catálogo",
            f"Añadió/Modificó producto '{material}' con precio {precio} GC"
        )
        return jsonify({
            "status": "success",
            "message": f"¡Recompensa '{material}' de {precio} GC registrada exitosamente en el catálogo!",
            "material": material,
            "precio": precio
        })
    except Exception as exc:
        return jsonify({"status": "danger", "message": f"Error al registrar la recompensa: {exc}"}), 500


@web_bp.post("/auditoria/congelar-wallet")
@requiere_rol("admin")
def congelar_wallet():
    from flask import jsonify
    if not _csrf_validar():
        return jsonify({"status": "danger", "message": "Token CSRF inválido"}), 400
        
    wallet_id = request.form.get("wallet_id", "")
    username = request.form.get("username", "")
    action = request.form.get("action", "") # "congelar" o "descongelar"
    
    if not wallet_id or not username or not action:
        return jsonify({"status": "danger", "message": "Datos incompletos para auditar billetera"}), 400
        
    try:
        user_id = obtener_usuario_id()
        if action == "congelar":
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE wallets SET estado = 'CONGELADA' WHERE id = %s", (wallet_id,))
                conn.commit()
                
            registrar_operacion_auditoria(
                user_id,
                "Control Billeteras",
                f"Billetera de '{username}' (ID: {wallet_id}) ha sido CONGELADA temporalmente por auditoría de cumplimiento."
            )
            return jsonify({
                "status": "warning",
                "message": f"La billetera de '{username}' ha sido CONGELADA en la bitácora de cumplimiento (DSM 3).",
                "wallet_id": wallet_id,
                "state": "CONGELADA"
            })
        else:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE wallets SET estado = 'ACTIVA' WHERE id = %s", (wallet_id,))
                conn.commit()

            registrar_operacion_auditoria(
                user_id,
                "Control Billeteras",
                f"Billetera de '{username}' (ID: {wallet_id}) ha sido reactivada."
            )
            return jsonify({
                "status": "success",
                "message": f"La billetera de '{username}' ha sido reactivada con éxito.",
                "wallet_id": wallet_id,
                "state": "ACTIVA"
            })
    except Exception as exc:
        return jsonify({"status": "danger", "message": f"Error al procesar control de billetera: {exc}"}), 500


@web_bp.post("/auditoria/fundear-wallet")
@requiere_rol("admin")
def fundear_wallet():
    from flask import jsonify
    if not _csrf_validar():
        return jsonify({"status": "danger", "message": "Token CSRF inválido"}), 400
        
    wallet_id = request.form.get("wallet_id", "")
    username = request.form.get("username", "")
    monto_str = request.form.get("monto", "0").strip()
    
    if not wallet_id or not username or not monto_str:
        return jsonify({"status": "danger", "message": "Datos incompletos para cargar saldo"}), 400
        
    try:
        monto = int(monto_str) * 100
        if monto <= 0:
            return jsonify({"status": "danger", "message": "El monto a cargar debe ser positivo"}), 400
            
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Incrementar saldo en base de datos
                cur.execute("UPDATE wallets SET saldo = saldo + %s WHERE id = %s", (monto, wallet_id))
                
                # Obtener nuevo saldo real
                cur.execute("SELECT saldo FROM wallets WHERE id = %s", (wallet_id,))
                wallet_row = cur.fetchone()
                nuevo_saldo = wallet_row["saldo"] if wallet_row else 0
                
                # 2. Registrar en la bitácora de auditoría
                user_id = obtener_usuario_id()
                registrar_operacion_auditoria(
                    user_id,
                    "Carga Administrativa",
                    f"Cargó administrativamente {monto / 100:.2f} GC a la billetera de '{username}' (Billetera ID: {wallet_id})"
                )
            conn.commit()
            return jsonify({
                "status": "success",
                "message": f"¡Carga de {monto / 100:.2f} GC a '{username}' realizada con éxito!",
                "wallet_id": wallet_id,
                "nuevo_saldo": nuevo_saldo
            })
    except Exception as exc:
        return jsonify({"status": "danger", "message": f"Error al realizar la carga de monedas: {exc}"}), 500




@web_bp.get("/auditoria/gestion-catalogo")
@requiere_rol("admin")
def gestion_catalogo():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    catalogo_items = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, material, precio/100.0 as precio FROM catalogo_recompensas ORDER BY material")
                cat_rows = cur.fetchall()
                for cr in cat_rows:
                    catalogo_items.append({
                        "id": cr["id"],
                        "material": cr["material"],
                        "precio": float(cr["precio"])
                    })
    except Exception:
        pass
    return render_template(
        "gestion_catalogo.html",
        catalogo_items=catalogo_items,
        current_user=current_user,
        saldo_actual=saldo_actual
    )


@web_bp.get("/auditoria/control-billeteras")
@requiere_rol("admin")
def control_billeteras():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    wallets_list = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT u.nombre_completo as usuario, u.email, w.clave_publica, w.saldo, w.estado, w.id as wallet_id "
                    "FROM usuarios u JOIN wallets w ON u.id = w.usuario_id WHERE u.rol = 'usuario' "
                    "ORDER BY u.nombre_completo"
                )
                wallet_rows = cur.fetchall()
                import hashlib as _hlw
                for wr in wallet_rows:
                    pk = wr["clave_publica"] or ""
                    wallets_list.append({
                        "id": wr["wallet_id"],
                        "usuario": wr["usuario"],
                        "email": wr["email"],
                        "clave_publica": pk,
                        "pk_alias": "PK-" + _hlw.sha256(pk.encode()).hexdigest()[:6].upper(),
                        "saldo": float(wr["saldo"]),
                        "estado": wr["estado"]
                    })
    except Exception:
        pass
    return render_template(
        "control_billeteras.html",
        wallets=wallets_list,
        current_user=current_user,
        saldo_actual=saldo_actual
    )


@web_bp.get("/auditoria/sensores-iot")
@requiere_rol("admin")
def sensores_iot():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template(
        "sensores_iot.html",
        current_user=current_user,
        saldo_actual=saldo_actual
    )


@web_bp.get("/configuracion")
@requiere_rol("usuario")
def configuracion():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("configuracion.html", current_user=current_user, saldo_actual=saldo_actual)


@web_bp.post("/configuracion")
@requiere_rol("usuario")
def configuracion_accion():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.configuracion"))

    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    user_id = obtener_usuario_id()

    if not nombre or not email:
        flash("Campos requeridos vacios", "danger")
        return redirect(url_for("web.configuracion"))

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET nombre_completo = %s, email = %s WHERE id = %s",
                    (nombre, email, user_id)
                )
            conn.commit()
        flash("Configuracion actualizada con exito", "success")
    except Exception as exc:
        flash(f"Error al actualizar la configuracion: {exc}", "danger")

    return redirect(url_for("web.configuracion"))


@web_bp.get("/ayuda")
@requiere_rol("usuario")
def ayuda():
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("ayuda.html", current_user=current_user, saldo_actual=saldo_actual)


@web_bp.get("/reciclar")
@requiere_rol("usuario")
def reciclar_form():
    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.dashboard"))
    current_user, saldo_actual = get_current_user_and_balance()
    return render_template("reciclar.html", current_user=current_user, saldo_actual=saldo_actual)


@web_bp.post("/reciclar")
@requiere_rol("usuario")
def reciclar_accion():
    if not _csrf_validar():
        flash("Token CSRF invalido", "danger")
        return redirect(url_for("web.reciclar_form"))

    if es_billetera_congelada():
        flash("⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).", "danger")
        return redirect(url_for("web.dashboard"))
    
    from app.core.rewards import registrar_recompensa_reciclaje
    from app.security.decorators import auditar, validar, firmar
    
    user_id = obtener_usuario_id()
    material = request.form.get("material", "Plástico PET")
    try:
        peso = float(request.form.get("peso", "1.0"))
        if peso <= 0:
            peso = 1.0
    except (ValueError, TypeError):
        peso = 1.0
    
    # Construir cartera del usuario actual desde BD
    cartera = {"saldo": 0}
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT saldo, clave_publica FROM wallets WHERE usuario_id = %s", (user_id,))
                wallet = cur.fetchone()
                if wallet:
                    cartera = {"saldo": int(wallet["saldo"]), "clave_publica": wallet["clave_publica"]}
    except Exception:
        pass
    
    # Construir catálogo desde BD
    catalogo = {}
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT material, precio FROM catalogo_recompensas")
                for row in cur.fetchall():
                    catalogo[row["material"]] = int(row["precio"])
    except Exception:
        pass

    @auditar
    @validar
    @firmar
    def _operacion():
        return registrar_recompensa_reciclaje(cartera, material, catalogo, peso)

    try:
        transaccion = _operacion()
        
        # Persistencia atómica en Base de Datos MariaDB
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Incrementar el saldo real de la wallet del usuario en DB
                neto_recompensa = transaccion["monedas_salida"][0]["valor"]
                cur.execute(
                    "UPDATE wallets SET saldo = saldo + %s WHERE clave_publica = %s",
                    (neto_recompensa, transaccion["origen"])
                )
                # 2. Insertar la transacción firmada y validada en el ledger
                import json
                import datetime
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    "INSERT INTO transacciones (tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        transaccion["tipo"].upper(),
                        transaccion["origen"],
                        transaccion["destino"],
                        json.dumps(transaccion["monedas_entrada"]),
                        json.dumps(transaccion["monedas_salida"]),
                        transaccion["impuesto"],
                        timestamp_str,
                        transaccion.get("firma", ""),
                        transaccion["estado"]
                    )
                )
            conn.commit()
            
        neto_display = float(neto_recompensa) / 100.0
        flash(f"Reciclaje registrado con éxito. Recompensa de {neto_display:.2f} GreenCoins acreditada.", "success")
    except NotImplementedError:
        flash("[STDD RED STATE] 'registrar_recompensa_reciclaje()' es un stub académico.", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infracción de contrato: {exc}", "danger")
    return redirect(url_for("web.reciclar_form"))


@web_bp.get("/historial")
@requiere_rol("usuario")
def historial():
    import json
    from app.auth.session import obtener_rol
    
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    transacciones = []
    rol = obtener_rol()
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if rol == "admin":
                    cur.execute(
                        "SELECT id, tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado "
                        "FROM transacciones "
                        "ORDER BY creado_en DESC"
                    )
                elif clave_publica:
                    cur.execute(
                        "SELECT id, tipo, origen, destino, monedas_entrada, monedas_salida, impuesto, timestamp, firma, estado "
                        "FROM transacciones "
                        "WHERE origen = %s OR destino = %s "
                        "ORDER BY creado_en DESC",
                        (clave_publica, clave_publica),
                    )
                else:
                    return render_template(
                        "historial.html",
                        current_user=current_user,
                        saldo_actual=saldo_actual,
                        transacciones=[]
                    )
                
                rows = cur.fetchall()
                for r in rows:
                    is_sender = (r["origen"] == clave_publica) if clave_publica else False
                    try:
                        # Para recompensas se muestra el neto (monedas_salida).
                        # Para compras se muestra el costo (monedas_entrada).
                        # Para transferencias:
                        # - Si eres emisor (sender), tu costo es monedas_entrada (monto + impuesto).
                        # - Si eres receptor (receiver), tu ganancia neta es monedas_salida (monto).
                        tipo_upper = r["tipo"].upper()
                        if tipo_upper == "RECOMPENSA":
                            campo_monedas = "monedas_salida"
                        elif tipo_upper == "COMPRA":
                            campo_monedas = "monedas_entrada"
                        else: # TRANSFER
                            campo_monedas = "monedas_entrada" if is_sender else "monedas_salida"
                        
                        coins = json.loads(r[campo_monedas])
                        val = sum(float(c.get("valor", 0)) for c in coins) / 100.0
                    except Exception:
                        val = 0.0

                    if tipo_upper == "COMPRA":
                        desc = f"Canje: {r['destino']}"
                        amount = -val
                    elif tipo_upper == "RECOMPENSA":
                        desc = "Recompensa por reciclaje"
                        amount = val
                    else:
                        if rol == "admin":
                            # Para el admin, mostrar direcciones resumidas para mayor legibilidad
                            ori_res = r["origen"][:16] + "..." if len(r["origen"]) > 16 else r["origen"]
                            dest_res = r["destino"][:16] + "..." if len(r["destino"]) > 16 else r["destino"]
                            desc = f"Transferencia: {ori_res} -> {dest_res}"
                            amount = val
                        else:
                            if is_sender:
                                desc = f"Enviado a {r['destino']}"
                                amount = -val
                            else:
                                desc = f"Recibido de {r['origen']}"
                                amount = val

                    transacciones.append({
                        "id": r["id"],
                        "date": r["timestamp"],
                        "type": r["tipo"],
                        "desc": desc,
                        "amount": amount,
                        "impuesto": float(r["impuesto"]) / 100.0,
                        "origen": r["origen"],
                        "destino": r["destino"],
                        "firma": r["firma"],
                        "estado": r["estado"],
                        "monedas_entrada": r["monedas_entrada"],
                        "monedas_salida": r["monedas_salida"]
                    })
    except Exception:
        pass

    return render_template(
        "historial.html",
        current_user=current_user,
        saldo_actual=saldo_actual,
        transacciones=transacciones
    )


@web_bp.post("/billetera/monedas")
@requiere_rol("usuario")
def obtener_monedas_virtuales():
    from flask import jsonify
    if not _csrf_validar():
        return jsonify({"status": "danger", "message": "Token CSRF invalido"}), 400

    user_id = obtener_usuario_id()
    wallet_id = request.form.get("wallet_id", "")

    saldo_raw = 0
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT saldo FROM wallets WHERE id = %s AND usuario_id = %s",
                    (wallet_id, user_id)
                )
                row = cur.fetchone()
                if row:
                    saldo_raw = int(row["saldo"])
    except Exception:
        pass

    if saldo_raw <= 0:
        return jsonify({"status": "ok", "monedas": []})

    monedas = []
    restante = saldo_raw
    fragmento = 100  # 1 GC = 100 centavos
    while restante > 0:
        valor = min(restante, fragmento)
        monedas.append({
            "id": f"GH-{uuid.uuid4().hex[:4].upper()}",
            "valor": valor
        })
        restante -= valor

    return jsonify({"status": "ok", "monedas": monedas})


@web_bp.get("/billetera")
@requiere_rol("usuario")
def billetera():
    current_user, saldo_actual, clave_publica = get_current_user_wallet_details()
    user_id = obtener_usuario_id()
    wallets_list = []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT w.id, w.saldo, w.clave_publica, w.creado_en "
                    "FROM wallets w WHERE w.usuario_id = %s "
                    "ORDER BY w.creado_en ASC",
                    (user_id,)
                )
                rows = cur.fetchall()
                for row in rows:
                    wallets_list.append({
                        "id": row["id"],
                        "saldo": float(row["saldo"]),
                        "clave_publica": row["clave_publica"],
                        "creado_en": row["creado_en"].strftime("%d/%m/%Y %H:%M") if row["creado_en"] else "N/A"
                    })
    except Exception:
        pass

    return render_template(
        "billetera.html",
        current_user=current_user,
        saldo_actual=saldo_actual,
        wallets_list=wallets_list
    )


@web_bp.post("/billetera/crear")
@requiere_rol("usuario")
def billetera_crear():
    if not _csrf_validar():
        flash("Token CSRF inválido", "danger")
        return redirect(url_for("web.billetera"))

    user_id = obtener_usuario_id()
    
    # Obtener nombre completo del usuario
    nombre = ""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nombre_completo FROM usuarios WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    nombre = row["nombre_completo"]
    except Exception:
        pass
    
    try:
        cartera = crear_cartera(nombre)
        
        # Insertar la wallet en BD con los datos devueltos por el stub
        clave_publica = cartera.get("clave_publica", secrets.token_urlsafe(32))
        clave_privada = cartera.get("clave_privada")
        saldo = cartera.get("saldo", 0)
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO wallets (usuario_id, clave_publica, clave_privada, saldo) VALUES (%s, %s, %s, %s)",
                    (user_id, clave_publica, clave_privada, saldo)
                )
            conn.commit()
        
        if clave_privada:
            session[f"priv_key_{clave_publica}"] = clave_privada
            session["clave_privada"] = clave_privada
        
        import hashlib as _hl
        pk_alias = "PK-" + _hl.sha256(clave_publica.encode()).hexdigest()[:6].upper()
        registrar_operacion_auditoria(user_id, "Crear Billetera", f"Nueva billetera EC-SECP256R1 creada | ID: {pk_alias}")
        flash(f"¡Billetera creada con éxito! Clave pública (EC-SECP256R1): {clave_publica[:40]}...", "success")
    except NotImplementedError:
        flash("'crear_cartera()' no está implementada todavía.", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infracción de contrato: {exc}", "danger")
    except Exception as exc:
        flash(f"Error al crear la billetera: {exc}", "danger")
    
    return redirect(url_for("web.billetera"))


@web_bp.post("/billetera/eliminar")
@requiere_rol("usuario")
def billetera_eliminar():
    if not _csrf_validar():
        flash("Token CSRF inválido", "danger")
        return redirect(url_for("web.billetera"))

    user_id = obtener_usuario_id()
    wallet_id = request.form.get("wallet_id", "")
    
    # Obtener cartera del usuario
    cartera = None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, saldo, clave_publica FROM wallets WHERE id = %s AND usuario_id = %s", (wallet_id, user_id))
                row = cur.fetchone()
                if row:
                    cartera = {"saldo": int(row["saldo"]), "clave_publica": row["clave_publica"]}
    except Exception:
        pass
    
    if not cartera:
        flash("No posees una billetera para eliminar", "warning")
        return redirect(url_for("web.billetera"))
    
    if cartera.get("saldo", 0) > 0:
        saldo_display = cartera["saldo"] / 100.0
        flash(f"No puedes eliminar una billetera con saldo activo ({saldo_display:.2f} GC). Transfiere o gasta el saldo primero.", "danger")
        return redirect(url_for("web.billetera"))

    try:
        resultado = eliminar_cartera(cartera)
        if resultado:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM wallets WHERE id = %s", (wallet_id,))
                conn.commit()
            registrar_operacion_auditoria(user_id, "Eliminar Billetera", f"Billetera (ID: {wallet_id}) eliminada. Claves revocadas.")
            flash("Billetera eliminada con éxito. Las claves criptográficas han sido revocadas.", "success")
        else:
            flash("No se pudo eliminar la billetera.", "warning")
    except icontract.ViolationError as exc:
        flash(f"Infracción de contrato: {exc}", "danger")
    except Exception as exc:
        flash(f"Error al eliminar la billetera: {exc}", "danger")
    
    return redirect(url_for("web.billetera"))


@web_bp.post("/billetera/consultar")
@requiere_rol("usuario")
def billetera_consultar():
    from flask import jsonify
    if not _csrf_validar():
        return jsonify({"status": "danger", "message": "Token CSRF inválido"}), 400

    user_id = obtener_usuario_id()
    wallet_id = request.form.get("wallet_id", "")
    
    # Obtener cartera del usuario
    cartera = None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT saldo, clave_publica FROM wallets WHERE id = %s AND usuario_id = %s", (wallet_id, user_id))
                row = cur.fetchone()
                if row:
                    cartera = {"saldo": int(row["saldo"]), "clave_publica": row["clave_publica"]}
    except Exception:
        pass
    
    if not cartera:
        return jsonify({"status": "warning", "message": "No posees una billetera activa.", "saldo": 0})

    # El dominio opera en unidades enteras de GC; la BD almacena centavos
    saldo_raw = cartera.get("saldo", 0)
    cartera_dominio = {"saldo": saldo_raw // 100, "clave_publica": cartera.get("clave_publica", "")}

    try:
        saldo = consultar_saldo(cartera_dominio)
        return jsonify({
            "status": "success",
            "message": f"Saldo verificado mediante contrato: {saldo} GC",
            "saldo": saldo
        })
    except icontract.ViolationError as exc:
        return jsonify({"status": "danger", "message": f"Infracción de contrato: {exc}", "saldo": 0})
