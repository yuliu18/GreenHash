# Guía de Ataques y Payloads para la Demostración de GreenHash

Este archivo contiene la lista de ataques mitigados y auditados de forma activa por el WAF y el sistema de control de autenticación de GreenHash. Utiliza estos payloads para demostrar la robustez de seguridad en tiempo real frente al tribunal/profesorado.

---

## 🔒 1. Inyección SQL (SQLi) — Mitigación DSM 4 (Bases de Datos)
El WAF inspecciona preventivamente la entrada y bloquea la consulta antes de que sea procesada en la base de datos MariaDB para evitar el bypass de login o exfiltración.

* **Dónde probarlo**: Campo de **"Correo electrónico"** en la pantalla de Login (`/auth/login`).
* **Payload a inyectar**:
  ```sql
  admin' OR 1=1 --
  ```
* **Qué ocurre al enviar**: 
  - La pantalla devuelve una página de error `400 Bad Request: Petición bloqueada por reglas del WAF de GreenHash.`
  - **Auditoría de Seguridad**: El sistema registra de forma anónima una entrada en la bitácora:
    - **Acción**: `SQLI_ATTEMPT`
    - **Detalle**: `Intento de inyección SQL mitigado en campo 'email'. Valor parcial: 'admin' OR 1=1 -...'` *(Se trunca automáticamente para cumplir con OWASP y no exponer datos sensibles)*.
    - **Estado**: `BLOQUEADO` 🔴

---

## 🌐 2. Cross-Site Scripting (XSS) — Mitigación DSM 1 (Web App)
El WAF intercepta etiquetas script e inyecciones de comandos HTML en los inputs de formularios para evitar el secuestro de cookies de sesión (Session Hijacking).

* **Dónde probarlo**: Campo de **"Nombre Completo"** en el formulario de Configuración (`/configuracion`) o en el formulario de Registro (`/auth/registro`).
* **Payload a inyectar**:
  ```html
  <script>alert('XSS')</script>
  ```
* **Qué ocurre al enviar**:
  - La pantalla devuelve una página de error `400 Bad Request`.
  - **Auditoría de Seguridad**: Se registra en la bitácora:
    - **Acción**: `XSS_ATTEMPT`
    - **Detalle**: `Intento de scripting XSS mitigado en campo 'nombre'. Valor parcial: '<script>alert('...'` *(Truncado por privacidad)*.
    - **Estado**: `BLOQUEADO` 🔴

---

## 🔑 3. Fuerza Bruta / Credential Stuffing — Mitigación DSM 1 (Web App)
Prevención de ataques de adivinación de contraseñas mediante bloqueo temporal de IP y tasa de intentos (Lockout).

* **Dónde probarlo**: Formulario de Login (`/auth/login`).
* **Acción de ataque**:
  - Intenta iniciar sesión con cualquier correo existente (ej: `CipherCoin@green.es`).
  - Introduce una **contraseña incorrecta 3 veces seguidas**.
* **Qué ocurre al 4to intento**:
  - El login se bloquea y muestra la alerta en rojo: `⚠️ Demasiados intentos fallidos. Tu cuenta ha sido bloqueada temporalmente por seguridad (DSM 1).`
  - **Auditoría de Seguridad**: Se registra una fila real:
    - **Acción**: `BRUTE_FORCE_ATTEMPT`
    - **Detalle**: `Fuerza bruta detectada en login para 'ciphercoin@g...'. Cuenta bloqueada temporalmente.` *(Privacidad respetada: contraseña no capturada y correo truncado)*.
    - **Estado**: `BLOQUEADO` 🔴

---

## 🚫 4. Uso de Cartera Congelada — Mitigación DSM 3 (GreenCoin)
Los fondos de la billetera e interacciones se deshabilitan por completo si la cuenta se congela por sospecha de fraude o desincronización.

* **Cómo probarlo**:
  1. Inicia sesión como administrador (`admin@greenhash.eco` / `admin`).
  2. Ve a **Control de Billeteras** (`/auditoria/control-billeteras`).
  3. Haz clic en **Congelar Cartera** para el usuario `CipherCoin`.
  4. En una ventana de incógnito, inicia sesión como `CipherCoin@green.es` e intenta hacer:
     - Un **Split** o **Merge** en la billetera (`/billetera`).
     - Registrar una recompensa de reciclaje (`/reciclar`).
* **Qué ocurre**:
  - El sistema muestra una alerta roja: `⚠️ Operación rechazada: Tu billetera se encuentra CONGELADA temporalmente por auditoría de cumplimiento (DSM 3).`
  - **Auditoría de Seguridad**: Se registran las acciones denegadas bajo estricto control de auditoría para su revisión por parte del analista de seguridad.
