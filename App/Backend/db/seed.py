"""Script para poblar la base de datos con los usuarios de la DEMO."""

import os
import sys

# Agregar el root del backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db_connection
from app.auth.helpers import hash_password
from app.core.wallet import crear_cartera

USUARIOS_DEMO = [
    {"nombre": "DidactionCoin", "email": "DidactionCoin@green.es", "pwd": "DidactionCoin", "rol": "usuario"},
    {"nombre": "ECTS", "email": "ECTS@green.es", "pwd": "ECTS", "rol": "usuario"},
    {"nombre": "CipherCoin", "email": "CipherCoin@green.es", "pwd": "CipherCoin", "rol": "usuario"},
    {"nombre": "UNICOIN", "email": "UNICOIN@green.es", "pwd": "UNICOIN", "rol": "usuario"},
    {"nombre": "Profesor Auditor", "email": "profesor@green.es", "pwd": "profesor", "rol": "admin"},
    {"nombre": "Admin General", "email": "admin@greenhash.eco", "pwd": "admin", "rol": "admin"},
]

CATALOGO_DEMO = [
    # Recompensas de la Tienda
    ("Silla Algas", 200),
    ("Mochila Eco", 100),
    ("Botella Verde", 100),
    ("Maceta Bio", 100),
    # Materiales de Reciclaje
    ("Plástico PET", 200),
    ("Aluminio / Latas", 500),
    ("Vidrio", 100),
    ("Papel y Cartón", 150),
]

def seed_database():
    print("Iniciando sembrado de la base de datos para la DEMO...")
    
    app = create_app()
    with app.app_context():
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Limpiar datos previos para asegurar un reset completo e impecable (consecución de consigna)
                print("[-] Limpiando tablas de base de datos para reset de la DEMO...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE auditoria;")
                cursor.execute("TRUNCATE TABLE transacciones;")
                cursor.execute("TRUNCATE TABLE wallets;")
                cursor.execute("TRUNCATE TABLE usuarios;")
                cursor.execute("TRUNCATE TABLE catalogo_recompensas;")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                # 1. Poblar usuarios y sus wallets
                for u in USUARIOS_DEMO:
                    print(f"[+] Creando usuario: {u['nombre']} ({u['rol']})")
                    pwd_hash = hash_password(u["pwd"])
                    
                    # Insertar usuario
                    cursor.execute(
                        "INSERT INTO usuarios (nombre_completo, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
                        (u["nombre"], u["email"], pwd_hash, u["rol"])
                    )
                    user_id = cursor.lastrowid
                    
                    # Crear wallet con clave EC-SECP256R1 real y 10.00 GreenCoins (1000 centavos)
                    cartera = crear_cartera(u["nombre"])
                    pub_key = cartera["clave_publica"]
                    cursor.execute(
                        "INSERT INTO wallets (usuario_id, clave_publica, saldo) VALUES (%s, %s, %s)",
                        (user_id, pub_key, 1000)
                    )

                # 2. Poblar catalogo
                for nombre, precio in CATALOGO_DEMO:
                    print(f"[+] Agregando al catalogo: {nombre}")
                    cursor.execute(
                        "INSERT INTO catalogo_recompensas (material, precio) VALUES (%s, %s)",
                        (nombre, precio)
                    )

            connection.commit()
    print("¡Sembrado completado con éxito!")

if __name__ == "__main__":
    seed_database()