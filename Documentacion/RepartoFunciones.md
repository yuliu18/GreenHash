# Informe de Reparto de Funciones y Trazabilidad (STDD)

Este documento detalla las **8 funciones críticas del Core de Dominio** de GreenHash diseñadas bajo la metodología **Security Test-Driven Development (STDD)**. Cada función representa un requerimiento de negocio y seguridad del modelado en Visual Paradigm (UML-S).

Con el fin de evitar confusiones al equipo de desarrollo ("coger mosca"), cada función tiene asignada su **ruta física, archivo de pruebas, acceso en la app web, y la especificación detallada de la lógica a programar**, haciendo especial hincapié en el cálculo y cobro de **impuestos y comisiones de red**.

---

## 📋 Cuadro de Distribución y Especificaciones de Lógica

### 🛡️ Módulo 1: Gestión de Billeteras (`app/core/wallet.py`)

#### 1. `crear_cartera(nombre_completo: str) -> dict`
* **Ubicación:** `App/Backend/app/core/wallet.py` (Línea 14)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_wallet.py` (`test_crear_cartera_no_implementado`)
* **Acceso y Simulación en la App:** En **Mi Billetera**, hacer clic en **"+ Crear nueva billetera"**.
* **⚙️ Lógica Detallada a Implementar:**
  1. Generar un par de claves criptográficas seguras (Pública y Privada) usando curvas elípticas (módulo `cryptography.hazmat`).
  2. Construir y retornar un diccionario que represente la billetera con el formato:
     ```python
     return {
         "nombre_completo": nombre_completo,
         "clave_publica": clave_publica_pem_string,
         "clave_privada": clave_privada_pem_string,
         "saldo": 0  # Toda billetera nueva inicia con saldo 0
     }
     ```

#### 2. `eliminar_cartera(cartera: dict) -> bool`
* **Ubicación:** `App/Backend/app/core/wallet.py` (Línea 22)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_wallet.py` (`test_eliminar_cartera_saldo_cero`)
* **Acceso y Simulación en la App:** En **Mi Billetera**, clic en el botón rojo de **"Eliminar Billetera"**.
* **⚙️ Lógica Detallada a Implementar:**
  1. **Regla de Seguridad Crítica:** Validar si `cartera.get("saldo", 0) == 0`.
  2. Si el saldo es mayor a 0, lanzar una excepción o retornar `False` (no se pueden destruir fondos activos).
  3. Si el saldo es exactamente 0, proceder a dar de baja criptográficamente la clave pública de los registros del sistema y retornar `True`.

#### 3. `consultar_saldo(cartera: dict) -> int`
* **Ubicación:** `App/Backend/app/core/wallet.py` (Línea 39)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_wallet.py` (`test_consultar_saldo_stub`)
* **Acceso y Simulación en la App:** Cargas asíncronas automáticas (AJAC) dentro del panel de **Mi Billetera**.
* **⚙️ Lógica Detallada a Implementar:**
  1. Recibir la billetera y verificar que contenga una firma o formato válido.
  2. Consultar la base de datos relacional filtrando por `clave_publica`.
  3. **Control de Desbordamiento:** Retornar el saldo como entero, asegurando que se encuentre en el rango permitido por contrato (`0 <= saldo <= LIMITE_MONEDAS_POR_CARTERA`).

---

### 💸 Módulo 2: Flujo Transaccional e Impuestos (`app/core/transactions.py`)

#### 4. `transferencia(origen: dict, destino_clave_publica: str, monto: int) -> dict`
* **Ubicación:** `App/Backend/app/core/transactions.py` (Línea 27)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_transactions.py` (`test_transferencia_monto_positivo`)
* **Acceso y Simulación en la App:** Panel **Transferir** (ingresar destinatario y monto).
* **⚙️ Lógica Detallada a Implementar y Cálculo de Impuestos:**
  1. **Validación de Fondos:** Verificar que `origen["saldo"] >= monto`.
  2. **Cálculo de Impuesto de Red:** Aplicar un impuesto del **5%** al monto total de la transferencia para financiar la red de validación.
     ```python
     impuesto = int(monto * 0.05)
     ```
  3. **Conservación de Valor:** Crear y firmar el bloque de la transacción. El total de monedas de salida (`monedas_salida`) debe ser exactamente igual a las monedas de entrada (`monedas_entrada`) más el impuesto registrado.
     * *Saldo Remitente (Decrementa):* `monto` + `impuesto`.
     * *Saldo Destinatario (Incrementa):* `monto`.
     * *Fondo del Sistema / Impuesto (Incrementa):* `impuesto`.
  4. Retornar el diccionario con la transacción firmada:
     ```python
     return {
         "tipo": "TRANSFER",
         "origen": origen["clave_publica"],
         "destino": destino_clave_publica,
         "monto": monto,
         "impuesto": impuesto,
         "firma": firma_criptografica,
         "estado": "VALIDA"
     }
     ```

#### 5. `split(cartera: dict, moneda_id: str, particiones: list) -> list`
* **Ubicación:** `App/Backend/app/core/transactions.py` (Línea 36)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_transactions.py` (`test_split_conservacion_valor`)
* **Acceso y Simulación en la App:** Pestaña **"Fraccionar (Split)"** en Mi Billetera.
* **⚙️ Lógica Detallada a Implementar:**
  1. Validar que la suma de los valores en la lista `particiones` sea exactamente igual al valor nominal de la moneda identificada por `moneda_id`.
  2. Destruir la moneda original en la base de datos (marcar como gastada/inactiva).
  3. Crear $N$ nuevas monedas fraccionarias con los montos indicados en `particiones`, vinculándolas a la clave pública de la cartera.
  4. Retornar la lista de las nuevas monedas creadas.

#### 6. `merge(cartera: dict, monedas_ids: list) -> dict`
* **Ubicación:** `App/Backend/app/core/transactions.py` (Línea 45)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_transactions.py` (`test_merge_conservacion_valor`)
* **Acceso y Simulación en la App:** Pestaña **"Fusionar (Merge)"** en Mi Billetera.
* **⚙️ Lógica Detallada a Implementar:**
  1. Validar que todas las monedas en `monedas_ids` pertenezcan a la cartera del usuario y no hayan sido gastadas previamente.
  2. Sumar el valor de todas las monedas especificadas.
  3. Marcar las monedas individuales como inactivas (destrucción lógica).
  4. Crear una única moneda consolidada con el valor total sumado.
  5. Retornar los detalles de la nueva moneda consolidada.

#### 7. `validar_transaccion(transaccion: dict, estado_sistema: dict) -> bool`
* **Ubicación:** `App/Backend/app/core/transactions.py` (Línea 50)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_transactions.py` (`test_validar_transaccion_stub`)
* **Acceso y Simulación en la App:** Automático a través del decorador `@requiere_firma_transaccion` en los endpoints del servidor Flask.
* **⚙️ Lógica Detallada a Implementar:**
  1. Recuperar la clave pública del emisor desde la transacción.
  2. Verificar criptográficamente la firma digital (`firma`) utilizando la clave pública y el contenido del bloque transaccional.
  3. **Validación del Impuesto:** Confirmar que el valor declarado en la columna `impuesto` coincida con las reglas de red (5% para transferencias, 10% para recompensas).
  4. Si la firma es válida y los impuestos/saldos son coherentes, retornar `True`; de lo contrario, retornar `False`.

---

### ♻️ Módulo 3: Recompensas de Reciclaje (`app/core/rewards.py`)

#### 8. `registrar_recompensa_reciclaje(cartera: dict, material: str, catalogo: dict) -> dict`
* **Ubicación:** `App/Backend/app/core/rewards.py` (Línea 16)
* **Archivo de Pruebas (STDD):** `App/Backend/tests/test_rewards.py` (`test_registrar_recompensa_stub`)
* **Acceso y Simulación en la App:** Sección **Reciclar** (seleccionar material, peso y hacer clic en Reclamar).
* **⚙️ Lógica Detallada a Implementar y Cálculo de Impuestos:**
  1. Consultar el precio por kilogramo del `material` dentro del catálogo de recompensas (DB o diccionario local `catalogo`).
  2. Calcular la recompensa base en función del peso depositado:
     ```python
     recompensa_base = peso_kg * precio_por_kg
     ```
  3. **Cobro de Impuesto Ecológico (Red):** Retener una comisión del **10%** en concepto de mantenimiento de los terminales físicos IoT:
     ```python
     impuesto = int(recompensa_base * 0.10)
     neto_a_depositar = recompensa_base - impuesto
     ```
  4. Incrementar el saldo de la `cartera` del reciclador con el valor neto obtenido.
  5. Registrar el bloque transaccional de tipo `"Recompensa"` en la base de datos, guardando explícitamente el `impuesto` retenido y firmando digitalmente la operación.
  6. Retornar el diccionario con el recibo de la transacción de reciclaje procesada.

---

## 🧪 Instrucciones para Ejecución de Pruebas (STDD)

Las pruebas unitarias del *core* corren tanto de forma **local** (recomendado para el ciclo rápido ROJO/VERDE, sin necesidad de Docker ni base de datos) como **dentro del contenedor**.

```bash
# --- Opción A: Local (sin Docker) ---
cd App/Backend
pytest                              # Todos los tests
pytest tests/test_wallet.py         # Solo billetera
pytest tests/test_transactions.py   # Solo transacciones (Split/Merge/Transfer)
pytest tests/test_rewards.py        # Solo reciclaje y recompensas

# --- Opción B: Dentro de Docker ---
cd App/Infra
docker-compose exec app pytest
docker-compose exec app pytest tests/test_wallet.py
```

## 🛡️ Análisis de Seguridad Estático (SAST)

Además de las pruebas funcionales, el proyecto integra **Bandit** (herramienta SAST) que analiza el código en busca de vulnerabilidades. Se ejecuta automáticamente en el CI en cada Pull Request.

```bash
# Instalar dependencias de desarrollo (incluye Bandit)
pip install -r App/Backend/requirements-dev.txt

# Ejecutar el análisis de seguridad
cd App/Backend
bandit -r app
```
*(Ver `Documentacion/InformeSAST.md` para el reporte completo de evidencia).*
