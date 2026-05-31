# Maqueta base y Especificación Técnica — GreenHash (Backend)

GreenHash es una aplicación web basada en una **Arquitectura Limpia / Hexagonal**, diseñada específicamente para mitigar riesgos de seguridad y mantener una estricta separación de responsabilidades (Separation of Concerns).

---

## 🏛️ Coherencia y Arquitectura del Proyecto

El sistema está organizado de manera sumamente coherente, separando dos grandes capas de desarrollo complementarias:
1. **`App/Frontend` (Maqueta de Diseño Visual):** Contiene los diseños preliminares estáticos y prototipos interactivos en React / JSX. Es la maqueta visual y pura que sirvió de base de diseño.
2. **`App/Backend` (Prototipo Funcional e Interactivo):** Es el corazón funcional de la entrega. Consiste en una aplicación web en Flask y MariaDB totalmente funcional que corre en Docker. Cuenta con seguridad criptográfica real, base de datos persistente, autenticación RBAC con sesiones y auditoría de inyecciones WAF.

---

## 🚀 Cómo ejecutar

```bash
cd App/Infra
docker-compose up --build
```
La aplicación queda expuesta en `http://localhost:5000`.

---

## 📂 Estructura General del Proyecto

```text
GreenHash/
├── EntregaFinal.vpp           # Base de datos SQLite que contiene los diagramas UML-S y de modelado
└── App/                       # Código fuente funcional del sistema
    ├── Infra/                 # Contenedores y orquestación
    │   └── docker-compose.yml # Levanta la app Flask y la base de datos MariaDB de forma aislada
    │
    ├── Frontend/              # Recursos visuales estáticos y prototipos JSX
    │   ├── static/            # CSS personalizado, imágenes de productos y avatares
    │   └── templates/         # Prototipos html puros
    │
    └── Backend/               # El núcleo lógico y operativo de GreenHash (Flask + Jinja2)
        ├── Dockerfile         # Configuración del contenedor de la aplicación
        ├── requirements.txt   # Dependencias de Python (Flask, icontract, cryptography, etc.)
        │
        ├── db/                # Capa de datos
        │   ├── schema.sql     # Definición de la estructura de tablas de la base de datos MariaDB
        │   └── seed.py        # Automatización de limpieza (Truncate) y usuarios semilla de la demo
        │
        ├── app/               # Código principal de la aplicación Flask
        │   ├── __init__.py    # Inicialización de Flask y la base de datos relacional
        │   │
        │   ├── core/          # 🛡️ CAPA DE DOMINIO (Reglas del Negocio Clave)
        │   │   ├── wallet.py        # Lógica pura de carteras (crear, borrar, saldos)
        │   │   ├── transactions.py  # Lógica transaccional (Split, Merge, Transfer, Firmas)
        │   │   └── rewards.py       # Lógica del cálculo de recompensas por reciclaje
        │   │
        │   ├── web/           # 💻 CAPA DE PRESENTACIÓN / VISTAS
        │   │   ├── routes.py  # Controladores de la interfaz (Tienda, Billetera, Historial, Auditoría WAF)
        │   │   └── templates/ # Plantillas HTML renderizadas con Jinja2
        │   │       ├── base.html        # Estructura maestra del sistema y alertas flotantes
        │   │       ├── login.html       # Interfaz de inicio de sesión limpia
        │   │       ├── billetera.html   # Panel dinámico de billeteras (Tabs: Split, Merge)
        │   │       ├── historial.html   # Libro contable histórico con filtros interactivos
        │   │       └── tienda.html      # Catálogo de recompensas
        │   │
        │   └── auth/          # 🔑 AUTENTICACIÓN Y SEGURIDAD DE SESIÓN
        │       └── routes.py  # Controladores de inicio de sesión y registro con tokens anti-CSRF
        │
        └── tests/             # 🧪 CAPA DE PRUEBAS AUTOMATIZADAS (STDD)
            ├── test_crypto.py       # Pruebas de firmado criptográfico digital
            ├── test_security.py     # Pruebas de validación de roles y accesos
            └── test_wallet.py / etc.# Casos de prueba para verificar contratos de negocio
```

---

## 🛡️ Los 3 Pilares del Diseño de Software Seguro en GreenHash

### 1. Diseño por Contrato (`Design by Contract`) en `app/core/`
En la capa `core` (Dominio), las operaciones clave están blindadas utilizando la biblioteca **`icontract`** para definir **Precondiciones (`@require`)** y **Postcondiciones (`@ensure`)** matemáticas y lógicas:
* **Precondiciones:** Garantizan que las funciones de negocio nunca se invoquen con estados de datos inválidos (por ejemplo, enviar montos negativos o transferir desde cuentas inexistentes).
* **Postcondiciones:** Aseguran que el estado final conserve invariantes del sistema (por ejemplo, que la suma total de GreenCoins en la red se mantenga constante antes y después de una transferencia, impidiendo ataques de doble gasto).

### 2. Strict TDD Mode (Desarrollo Guiado por Pruebas Estricto)
La suite de pruebas contiene **20 tests automatizados** bajo pytest que validan rigurosamente el comportamiento seguro del sistema:
* **12 Tests en Verde (Green):** Verifican la mitigación de SQL injection, la solidez del cifrado de firmas digitales, el control de roles y los flujos seguros del WAF y las cookies.
* **8 Tests en Rojo (Red / NotImplementedError):** Diseñados de forma determinista para las funciones core stubs. Esto asegura el flujo correcto del equipo de desarrollo, donde los stubs exponen firmas válidas pero previenen accesos no implementados, mientras la interfaz web maneja las alertas de forma grácil sin producir caídas catastróficas.

### 3. Aislamiento e Infraestructura Segura (`Infra/`)
Alineado con los modelos **DSM (Domain Security Models)** en UML-S:
* La aplicación se despliega mediante **Docker Compose**, aislando el servidor Flask del motor relacional MariaDB de manera que no hay exposición directa del puerto de base de datos a internet.
* La base de datos es inicializada de forma idéntica en cada despliegue a través del script `seed.py`, el cual realiza truncados seguros (`TRUNCATE`) y limpia registros residuales para garantizar demostraciones 100% confiables y reproducibles con los saldos iniciales exactos del informe (10 GreenCoins).

---

## 📍 Shell vs. Stubs

- **Shell**: Rutas Flask, templates Jinja2 interactivos, auth con tokens de sesión criptográficos, controles de rol (RBAC) y decoradores WAF.
- **Stubs**: `app/core/` contiene las firmas + contratos con `icontract`. Todas las funciones de lógica profunda lanzan `NotImplementedError` para forzar el ciclo TDD.

---

## 🗺️ Mapa de Rutas, Templates y Variables de la Maqueta

| Ruta | Template | Variables | Descripción / Acceso |
| --- | --- | --- | --- |
| GET / | `index.html` | Ninguna | Página de inicio (Landing page pública) |
| GET /auth/login | `login.html` | Ninguna | Panel de ingreso con credenciales de la demo visibles |
| GET /auth/registro | `registro.html` | Ninguna | Formulario de registro de nuevos usuarios |
| GET /dashboard | `dashboard.html` | `saldo_actual`, `transacciones` | Panel general del reciclador con resumen del saldo global |
| GET /billetera | `billetera.html` | `billeteras`, `transacciones` | Gestor de múltiples wallets (Tabs: General, Split, Merge) |
| GET /tienda | `tienda.html` | `catalogo` | Catálogo interactivo de productos y comprobante de entrega |
| GET /historial | `historial.html` | `transacciones` | Libro de transacciones con filtros dinámicos (Rol: Usuario / Admin) |
| GET /auditoria | `auditoria.html` | `registros` | Consola de Auditoría WAF (Logs interactivos de SQLi/XSS) |
| GET /beneficios | `beneficios.html` | Ninguna | Sección informativa de beneficios gubernamentales |

---

## 🌿 Ramas para la Implementación STDD

Cada una de las ramas de desarrollo corresponde a un módulo del núcleo de seguridad y negocio:
* `feat/transferencia`
* `feat/split`
* `feat/merge`
* `feat/validacion`
* `feat/crypto`
* `feat/recompensas`
* `feat/auditoria`
* `feat/wallet`

Cada integrante toma una rama, trabaja sobre su archivo correspondiente en `app/core/` y se asegura de dejar en color **VERDE** los tests correspondientes en la suite.
