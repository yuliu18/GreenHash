# Flujo de Trabajo del Equipo (STDD)

Este documento detalla el paso a paso que cada integrante del equipo debe seguir para implementar su función asignada siguiendo la práctica de Security Test-Driven Development (STDD).

## 1. Clonar y Preparar el Entorno

Primero, bajate el repositorio y levantá el sistema completo usando Docker. Esto asegura que tengas la base de datos lista y el entorno configurado sin tener que instalar cosas raras en tu PC.

### Configuración de Variables de Entorno (¡Importante!)
Para evitar subir credenciales secretas al repositorio de código (siguiendo las prácticas seguras de **OWASP** y **12-Factor App**), el proyecto utiliza un archivo de configuración `.env`. 

Antes de empezar, debés crear tu archivo local `.env` a partir de la plantilla provista:
```bash
# 1. Pararse en la carpeta del backend
cd App/Backend

# 2. Copiar la plantilla para crear tu archivo local .env
cp .env.example .env
```
*(Nota: Si usás Docker, el archivo `docker-compose.yml` ya inyecta estos parámetros automáticamente para levantar la base de datos y la aplicación Flask de forma integrada. Sin embargo, tener el archivo `.env` configurado es una excelente práctica para que tu entorno virtual y editores de código reconozcan las variables).*

### Levantar con Docker

```bash
# 1. Clonar el repo
git clone <URL_DEL_REPOSITORIO>
cd GreenHash

# 2. Copiar el archivo .env (explicado en el paso anterior)
cd App/Backend && cp .env.example .env && cd ../..

# 3. Levantar la aplicación con Docker (dejalo corriendo en una terminal)
cd App/Infra
docker-compose up --build
```

*Nota: Podés instalar las librerías localmente creando un entorno virtual en `App/Backend` si querés que tu editor de código (VSCode, PyCharm) te autocomplete el código. Las pruebas unitarias del core (contratos y lógica de dominio) corren perfectamente de forma local sin Docker ni base de datos. Solo necesitás Docker para probar los flujos completos de la interfaz web.*

## 2. Cambiar a tu Rama Asignada

Cada integrante tiene una rama predefinida con el formato `ramaN/apellidos`. **Nadie programa directamente en `main`**.

```bash
# Actualizar el listado de ramas del servidor
git fetch

# Cambiar a tu rama (reemplazá con tu número y apellidos reales)
git checkout ramaN/apellidos
```

## 3. Implementación STDD (De Rojo a Verde)

Tu tarea es implementar una función del *core* del dominio, ubicada en `App/Backend/app/core/`. El cascarón web ya está conectado, pero ahora mismo tu función lanza un `NotImplementedError`.

La dinámica es guiada por pruebas:

1. **Mirar el fallo (ROJO)**: Identificá el archivo de test que te toca en `App/Backend/tests/` (por ejemplo, `test_transactions.py`). Las pruebas del core corren localmente sin necesidad de Docker ni base de datos.
   ```bash
   # Opción A — Local (recomendada para el ciclo ROJO/VERDE rápido)
   cd App/Backend
   pytest tests/test_tu_archivo.py

   # Opción B — Dentro de Docker (si querés probar también la integración con la BD)
   cd App/Infra
   docker-compose exec app pytest tests/test_tu_archivo.py
   ```

2. **Escribir el código**: Abrí tu editor de código (VSCode) y andá a tu archivo en `App/Backend/app/core/`. Implementá la lógica borrando el `raise NotImplementedError`.
   *⚠️ Importante: Respetá los decoradores `@require` y `@ensure` de `icontract` que ya están puestos. Son reglas inquebrantables de seguridad y negocio (ej: que el saldo sea positivo, que el monto no supere el límite permitido, etc.).*

3. **Verificar el éxito (VERDE)**: Volvé a correr el mismo comando del test. Si falla, corregí tu código. Si pasa, estás listo para subir.
   ```bash
   # Local — sin Docker
   cd App/Backend
   pytest tests/test_tu_archivo.py
   ```

## 4. Subir Cambios y Crear Pull Request (PR)

Una vez que tus tests están en verde localmente, subís tu trabajo para revisión.

```bash
# 1. Verificar qué archivos tocaste (para no subir cosas de más)
git status

# 2. Agregar tus cambios
git add .

# 3. Crear un commit descriptivo
git commit -m "feat: implementar logica de transferencia y split"

# 4. Subir los cambios de tu rama a GitHub
git push origin ramaN/apellidos
```

Después del push, entrá a GitHub y **creá un Pull Request (PR)** desde tu rama `ramaN/apellidos` apuntando a `main`.

## 5. Revisión y CI (Integración Continua)

Una vez creado el PR, GitHub Actions ejecuta automáticamente el pipeline definido en `.github/workflows/ci.yml`, que consta de **dos trabajos (jobs)**:

### 5.1. Job `SAST (Bandit)` — Gate de Seguridad (BLOQUEANTE)
Es el control de seguridad principal y **decide si el PR pasa en verde o rojo**:
- Ejecuta **Bandit** (herramienta SAST) sobre el código fuente buscando vulnerabilidades.
- **Bloquea la integración (rojo)** únicamente si detecta vulnerabilidades de severidad **Media o Alta**.
- Los hallazgos de severidad Baja se reportan pero no bloquean.
- *(Ver `Documentacion/InformeSAST.md` para el detalle de la metodología y resultados).*

### 5.2. Job `Tests (pytest STDD)` — Informativo (NO bloqueante)
- Ejecuta la suite de pruebas `pytest`.
- Está configurado como `continue-on-error`, por lo que **los 8 stubs en estado RED (`NotImplementedError`) NO bloquean el PR**. Esto es intencional: bajo la metodología Strict TDD, esos tests en rojo documentan las funciones del *core* que aún están pendientes de implementar.
- A medida que cada integrante implementa su función en su rama, su test correspondiente pasa a verde de forma natural.

### 5.3. Flujo de revisión
1. **Revisión de Código (Code Review)**: El líder del proyecto revisará tu código buscando vulnerabilidades (inyección SQL, lógica de negocio rota, evasión de contratos `icontract`).
2. **Correcciones**: Si te dejan comentarios pidiendo cambios, **no cierres ni crees otro PR**. Hacé los arreglos en tu compu, volvé a hacer `git add`, `git commit` y `git push`. El PR se actualiza automáticamente.
3. **Merge**: Una vez que el gate SAST está en verde y el código está aprobado, el líder hace el merge a `main`.