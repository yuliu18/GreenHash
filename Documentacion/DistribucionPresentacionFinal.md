# Distribución y Guion de la Presentación Final — Proyecto GreenHash

**Asignatura:** Ingeniería del Software Seguro  
**Estructura:** 21 Diapositivas (Plantilla Oficial ISS 25/26)

---

### Slide 01: Portada y Título
* **Ponente:** Yuchun

### Slide 02: Contenido / Índice recomendado
* **Ponente:** Yuchun

### Slide 03: El contexto del Reciclaje
* **Ponente:** Yuchun

### Slide 04: Vulnerabilidades y problemas del sector
* **Ponente:** Kike

### Slide 05: La solución GreenHash
* **Ponente:** Kike

### Slide 06: Análisis de partes y punto de vista (Tropos Secure) - I
* **Ponente:** Iván

### Slide 07: Análisis de partes y punto de vista (Tropos Secure) - II
* **Ponente:** Iván

### Slide 08: El caso de uso y mal uso
* **Ponente:** Enrique

### Slide 09: Requisitos (funcionales y no funcionales)
* **Ponente:** Enrique

### Slide 10: Modelo de dominio (Domain Class Diagrams) - I
* **Ponente:** Alejandro

### Slide 11: Modelo de dominio (Domain Class Diagrams) - II
* **Ponente:** Alejandro

### Slide 12: Domain Security Model (DSM) - Web & Mobile Application
* **Ponente:** Kian

### Slide 13: Otro DSM (GreenCoin, Punto de Recogida y Operarios)
* **Ponente:** Kian

---

### Slide 14: Desarrollo Seguro — Criptografía Asimétrica y Diseño por Contrato
* **Ponente:** Jesús
* **Contenido a explicar:**
  * Uso de firmas ECDSA basadas en curvas elípticas estándar (`secp256r1`) para mitigar la suplantación de identidad en las transferencias de GreenCoins.
  * Implementación de **Diseño por Contrato (`icontract` en Python)** en el backend para blindar las reglas matemáticas críticas de balance y preservación de valor en las transacciones `SPLIT` y `MERGE` (precondiciones, postcondiciones e invariantes).

### Slide 15: Desarrollo Seguro — Principio de Mínimo Privilegio (RBAC)
* **Ponente:** Jesús
* **Contenido a explicar:**
  * Aplicación del principio de mínimo privilegio mediante control de accesos basado en roles (RBAC) tanto en las rutas del API en el Backend de Flask como a nivel de base de datos MariaDB (aislamiento estricto de usuarios y permisos).

### Slide 16: Desarrollo Seguro — Defensa en Profundidad (WAF Middleware)
* **Ponente:** Jesús
* **Contenido a explicar:**
  * Diseño e implementación del middleware WAF (Web Application Firewall) en Flask para interceptar y bloquear ataques de inyección (SQLi y XSS) en la capa de red antes de que las peticiones toquen la base de datos o la lógica de negocio.

### Slide 17: Pruebas de Seguridad — Metodología STDD
* **Ponente:** Yusen
* **Contenido a explicar:**
  * Introducción de la metodología **Security Test-Driven Development (STDD)** adoptada en el proyecto: cómo las pruebas de seguridad y de lógica transaccional se escribieron primero (Fase Roja) para guiar el desarrollo posterior de las soluciones (Fase Verde).

### Slide 18: Pruebas de Seguridad — Verificación Dinámica de Código
* **Ponente:** Yusen
* **Contenido a explicar:**
  * Ejecución de la suite de 44 pruebas de seguridad automatizadas en `pytest`.
  * Explicación de la trazabilidad académica del prototipo, demostrando cómo los stubs del sistema transicionaron visualmente en las vistas del usuario desde `[STDD ESTADO ROJO]` (pendiente/simulado) a `[STDD ESTADO VERDE]` (implementado y verificado en tiempo de ejecución).

### Slide 19: Pruebas de Seguridad — Análisis Estático (SAST) y Pipeline de CI/CD
* **Ponente:** Yusen
* **Contenido a explicar:**
  * Detallar la integración de **Bandit** (herramienta SAST) en el flujo de integración continua (GitHub Actions), actuando como un gate de seguridad bloqueante automatizado que impide integrar código con vulnerabilidades a la rama `main`.

### Slide 20: Conclusión y Cierre
* **Ponente:** Yuchun
* **Contenido a explicar:**
  * Resumen de la experiencia, lecciones aprendidas sobre el diseño seguro de software y la importancia de proteger el entorno de la economía circular ("No hay Planeta B").

### Slide 21: Preguntas y Cierre de la Presentación
* **Ponente:** Yuchun
* **Contenido a explicar:**
  * Apertura del espacio de preguntas y respuestas para el tribunal evaluador y despedida del grupo.
