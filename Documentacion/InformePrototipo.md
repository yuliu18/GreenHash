# Informe del Prototipo e Interfaz Web de GreenHash

Este documento describe de forma completa el **funcionamiento, la estructura de páginas, la lógica del negocio, el esquema de la base de datos relacional y las medidas de seguridad** del prototipo interactivo desarrollado para la materia de **Ingeniería de Software Seguro**. 

Actualiza y consolida las especificaciones preliminares de diseño, adaptándolas a las implementaciones de seguridad de producción, mitigación de fraudes y la arquitectura definitiva basada en **Jinja2, Flask y MariaDB**.

---

## 🏛️ 1. Estructura y Vistas de la Aplicación

La aplicación consta de **7 páginas/vistas principales** que modelan todo el ciclo operativo de incentivos criptográficos:

1. **Página de Inicio (Login):** Panel de acceso centralizado. Se ha eliminado cualquier texto redundante para mantener una estética minimalista. Incluye un cuadro informativo con las credenciales de los 6 perfiles seeded de la demo.
2. **Dashboard / Menú Principal:** Resumen interactivo del estado del reciclador. Muestra de forma clara y en gran tamaño el saldo disponible en GreenCoins (GC), accesos directos a las operaciones y un panel lateral de navegación coherente con los modelos de diseño.
3. **Página de Transferencias:** Interfaz para enviar GreenCoins entre billeteras (Peer-to-Peer). Requiere ingresar la clave pública de destino y la cantidad, aplicando automáticamente una **tasa de red de validación (impuesto del 5%)**.
4. **Página de Reciclaje:** Simulador interactivo de la báscula física IoT. Permite seleccionar el material y el peso ingresado para calcular dinámicamente y en tiempo real el saldo base, la **tasa de red ecológica (impuesto del 10%)** y el depósito neto.
5. **Catálogo (Tienda):** Catálogo de recompensas sostenibles donde los usuarios canjean sus GreenCoins acumulados. Incluye modales centrados para ver detalles de los productos (Silla Algas, Mochila Eco, etc.).
6. **Consulta de Materiales:** Interfaz de búsqueda parametrizada que lista los materiales aceptados por la red y su equivalente de incentivo por Kg.
7. **Historial de Actividad (Contabilidad):** Libro contable interactivo con filtros dinámicos (Desde, Hasta, Tipo). 
   * **Usuarios:** Ven únicamente su propio historial transaccional de forma segura.
   * **Administradores y Profesores:** Tienen acceso al panel de **Auditoría Global (Ledger)** y a la consola de **Auditoría WAF** (intentos bloqueados de SQLi/XSS).

---

## 🗄️ 2. Estructura y Esquema de Base de Datos (MariaDB)

La persistencia de datos está estructurada de forma relacional y robusta en MariaDB bajo el siguiente esquema de tablas (`db/schema.sql`):

### 1. Tabla `usuarios`
Almacena las identidades y credenciales de acceso de la red:
* `id` (INT, Autoincremental, Primary Key)
* `nombre_completo` (VARCHAR)
* `email` (VARCHAR, Único, llave de acceso)
* `password_hash` (VARCHAR, Contraseña cifrada de forma segura con PBKDF2)
* `rol` (VARCHAR, Control de accesos RBAC: 'usuario' o 'admin')
* `creado_en` (TIMESTAMP)

### 2. Tabla `wallets`
Vincula de forma segura a los usuarios con sus fondos y estado criptográfico:
* `id` (INT, Autoincremental, Primary Key)
* `usuario_id` (INT, Foreign Key referencing `usuarios(id)`)
* `clave_publica` (VARCHAR, Clave pública única del usuario en formato RSA PEM)
* `saldo` (INT, Balance disponible en GreenCoins)
* `estado` (VARCHAR, Control de estado contable: 'ACTIVA' o 'CONGELADA')
* `creado_en` (TIMESTAMP)

### 3. Tabla `transacciones`
El ledger centralizado e inmutable del sistema:
* `id` (INT, Autoincremental, Primary Key)
* `tipo` (VARCHAR, Tipo de movimiento: 'TRANSFER', 'COMPRA', 'RECOMPENSA')
* `origen` (VARCHAR, Clave pública emisora)
* `destino` (VARCHAR, Clave pública receptora)
* `monedas_entrada` (TEXT, Monedas de entrada referenciadas)
* `monedas_salida` (TEXT, Monedas resultantes del fraccionamiento/salida)
* `impuesto` (INT, Comisión cobrada por la red: 5% en transferencias, 10% en reciclaje)
* `timestamp` (VARCHAR, Marca de tiempo de la transacción)
* `firma` (TEXT, Firma criptográfica digital elíptica que asegura no-repudio)
* `estado` (VARCHAR, Estado de la transacción: 'VALIDA', 'PENDIENTE', 'RECHAZADA')
* `creado_en` (TIMESTAMP)

### 4. Tabla `catalogo_recompensas`
Catálogo de precios de los productos y materiales permitidos:
* `id` (INT, Autoincremental, Primary Key)
* `material` (VARCHAR, Nombre único del producto/material)
* `precio` (INT, Coste en GreenCoins o valor de incentivo por Kg)
* `actualizado_en` (TIMESTAMP)

### 5. Tabla `auditoria`
Logs de auditoría del WAF y acciones administrativas críticas:
* `id` (INT, Autoincremental, Primary Key)
* `usuario_id` (INT, Opcional, ID del administrador que ejecuta la acción)
* `operacion` (VARCHAR, Módulo afectado, ej. 'Control Billeteras', 'WAF')
* `detalles` (TEXT, Descripción del evento bloqueado o registrado)
* `creado_en` (TIMESTAMP)

---

## 🛡️ 3. Reglas de Negocio, Roles y Mitigación de Fraudes

### 👥 Matriz de Roles y Accesos del Sistema

| Rol | Modificar Catálogo | Visualizar Auditoría WAF | Congelar/Descongelar Wallets | Bloqueo de Operaciones |
| :--- | :---: | :---: | :---: | :---: |
| **Usuario Reciclador** | NO | NO | NO | Afectado por Congelamiento |
| **Profesor Auditor** | NO | SI | NO | NO |
| **Administrador General** | SI | SI | SI | SI (Puede Congelar) |

### 🔒 Política de Congelamiento de Carteras (Mitigación de Fraudes DSM 3)
El Administrador General tiene privilegios para **Congelar lógicamente** la cartera de cualquier reciclador de forma persistente en la base de datos si se detectan anomalías de pesaje IoT o intentos de doble gasto:
1. **Persistencia:** Al congelar, se realiza un `UPDATE` en la tabla `wallets` cambiando `estado = 'CONGELADA'` y se asienta un log inmutable en la tabla `auditoria`.
2. **Visualización:** El usuario afectado visualiza un **banner rojo de advertencia persistente** en la cabecera de todas sus páginas.
3. **Bloqueo Total de Salida:** Se bloquea físicamente en el backend cualquier acción de salida de fondos: **Transferencias, Canje de Tienda, Splits (Fraccionamientos) y Merges (Fusiones)**. Si intenta evadir la interfaz, el servidor Flask rechaza la petición enviando una alerta roja y manteniendo sus activos bloqueados de forma segura.

### 🧾 Política de Comisiones e Impuestos de Red
El cobro de tasas está integrado de forma transparente e inmutable en el backend:
* **Transferencias (5%):** El emisor abona `monto + 5%` de impuesto de red, incrementando el saldo del destinatario en `monto` y sumando el `5%` al tesoro central.
* **Recompensas de Reciclaje (10%):** Al registrar un depósito (ej. Plástico a 2 GC/Kg), se calcula la recompensa base y se deduce un **10% de Impuesto Ecológico** para el mantenimiento de los terminales físicos autorizados (DSM 5), depositando el saldo neto (`base - 10%`) de forma firmada en su wallet.

---

## 🧪 4. Trazabilidad del Core Académico (Strict TDD Mode)

Las **8 funciones críticas** de negocio y seguridad están definidas como stubs en la capa de dominio (`app/core/`) y protegidas por contratos inquebrantables con **`icontract`**:

1. **`crear_cartera()`** (en `app/core/wallet.py`) -> Genera claves criptográficas y saldo inicial 0.
2. **`eliminar_cartera()`** (en `app/core/wallet.py`) -> Valida saldo cero antes de borrar.
3. **`consultar_saldo()`** (en `app/core/wallet.py`) -> Consulta balance en DB relacional de forma segura.
4. **`transferencia()`** (en `app/core/transactions.py`) -> Valida fondos, deduce impuestos de red y firma.
5. **`split()`** (en `app/core/transactions.py`) -> Fracciona denominaciones de monedas.
6. **`merge()`** (en `app/core/transactions.py`) -> Consolida monedas fraccionadas individuales.
7. **`validar_transaccion()`** (en `app/core/transactions.py`) -> Valida firmas criptográficas digitales.
8. **`registrar_recompensa_reciclaje()`** (en `app/core/rewards.py`) -> Calcula recompensa y retiene el 10% del impuesto ecológico.
