# Informe de Análisis de Seguridad Estático (SAST) — GreenHash

Este documento constituye la **evidencia de ejecución de la herramienta SAST** (Static Application Security Testing) requerida para la entrega de la materia **Ingeniería de Software Seguro**.

---

## 1. ¿Qué es SAST y por qué se usa?

El **Análisis Estático de Seguridad de Aplicaciones (SAST)** consiste en inspeccionar el código fuente **sin ejecutarlo**, buscando patrones que representen vulnerabilidades de seguridad (inyecciones, criptografía débil, secretos hardcodeados, manejo inseguro de excepciones, etc.).

Se diferencia de las pruebas funcionales (`pytest`), que verifican *si el código hace lo correcto*. SAST verifica *si el código es seguro*. Ambas son complementarias y forman parte de un pipeline de **DevSecOps**.

---

## 2. Herramienta Utilizada: Bandit

* **Herramienta:** [Bandit](https://bandit.readthedocs.io/) — estándar de la industria para SAST en proyectos Python.
* **Versión:** `1.7.9`
* **Alcance del escaneo:** `App/Backend/app/` (capa de dominio, web, seguridad y autenticación).
* **Mapeo de hallazgos:** Cada hallazgo se clasifica según su identificador Bandit (`Bxxx`) y su correspondiente categoría **CWE** (Common Weakness Enumeration).

### Comando de ejecución

```bash
# Instalación
pip install -r App/Backend/requirements-dev.txt

# Ejecución del escaneo completo
cd App/Backend
bandit -r app

# Gate de seguridad (falla solo ante severidad Media o Alta)
bandit -r app --severity-level medium --confidence-level medium

# Generar reporte visual en HTML (para evidencia/capturas)
bandit -r app -f html -o reporte_sast.html
```

> 📎 **Evidencia visual adjunta:** El reporte completo y navegable de esta ejecución se encuentra en [`reporte_sast.html`](./reporte_sast.html) (en esta misma carpeta `Documentacion/`). Abrilo en cualquier navegador para ver el detalle interactivo de los hallazgos.

---

## 3. Resultado de la Ejecución (Evidencia)

```
Run started: 2026-05-31

Test results:
        No issues identified. (severidad Media/Alta)

Code scanned:
        Total lines of code: 1421

Run metrics:
        Total issues (by severity):
                High:   0
                Medium: 0
                Low:    16
```

### Resumen de severidades

| Severidad | Hallazgos | Estado |
| :--- | :---: | :--- |
| 🔴 **Alta (High)** | **0** | ✅ Sin vulnerabilidades críticas |
| 🟠 **Media (Medium)** | **0** | ✅ Sin vulnerabilidades de riesgo medio |
| 🟡 **Baja (Low)** | 16 | ⚠️ Revisadas y aceptadas (ver análisis) |

**Veredicto del Gate de Seguridad:** ✅ **APROBADO** (`exit code 0`). El código no presenta vulnerabilidades de severidad Media ni Alta.

---

## 4. Análisis de los Hallazgos de Severidad Baja

Los **16 hallazgos** detectados son **todos del mismo tipo** y han sido revisados y clasificados como **riesgo aceptado**:

| Identificador | CWE | Descripción | Ubicación |
| :--- | :--- | :--- | :--- |
| `B110: try_except_pass` | CWE-703 (Manejo inadecuado de excepciones) | Bloques `try / except: pass` | `app/web/routes.py` (14 casos), `app/core/rewards.py` (2 casos) |

### Justificación técnica (Riesgo Aceptado)

Estos bloques `try/except: pass` implementan un patrón intencional de **degradación controlada (graceful degradation)** en las lecturas no críticas a la base de datos. 

* **Propósito:** Si una consulta de lectura secundaria (por ejemplo, cargar el catálogo o el saldo para mostrar en pantalla) falla momentáneamente, la aplicación **no debe colapsar** ni exponer un *stack trace* al usuario (mitigando además **CWE-209: Exposición de información por mensajes de error**).
* **Por qué es de severidad Baja:** Bandit lo marca porque silenciar excepciones *podría* ocultar errores. En este contexto académico/maqueta es una decisión deliberada de robustez de la interfaz.
* **Acción correctiva futura:** En un entorno productivo, estos bloques evolucionarían para registrar el error en un sistema de *logging* centralizado (ej. `logger.warning(...)`) en lugar de descartarlo silenciosamente.

---

## 5. Integración Continua (CI/CD) — DevSecOps

El análisis SAST está **automatizado** en el pipeline de Integración Continua (`.github/workflows/ci.yml`). En cada Pull Request hacia `main`, GitHub Actions ejecuta automáticamente el escaneo de Bandit:

* El **Gate de Seguridad** bloquea la integración (marca el PR en rojo) si aparece cualquier vulnerabilidad de severidad **Media o Alta**.
* Esto garantiza que ningún código con vulnerabilidades relevantes pueda fusionarse a la rama principal, cumpliendo el principio de **Seguridad por Diseño (Security by Design)**.
