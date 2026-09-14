# AGENTS.md

Guía operativa para agentes de código en este repositorio. Léela entera antes de
escribir nada.

---

## 1. El dominio: qué es una MIR

**MIR** = **M**ejora, **I**ncidencia o **R**eclamación.

Este backend implementa el procedimiento **PG09 "Procedimiento general de
gestión de mejoras, incidencias y reclamaciones"** de AINIA (rev. 14). Sustituye
al aplicativo histórico "Gestión MIR" sobre IBM Lotus.

Una MIR es cualquier desviación, oportunidad de mejora o insatisfacción
detectada en la organización, que se registra y se lleva hasta su resolución en
un plazo máximo orientativo de **3-4 meses**. El PG09 es la fuente de verdad del
dominio: ante cualquier duda de comportamiento, manda el PG09, no la intuición.

### 1.1 Roles

| Rol | Descripción |
| --- | --- |
| **Detector** | Cualquier persona de la organización. Registra la MIR. |
| **Jefe de CLD** | Recibe la MIR registrada y designa al técnico de CLD que la gestiona. |
| **Técnico de CLD** | Dueño del ciclo: evalúa, clasifica, aprueba acciones, cierra, hace la CE y finaliza. |
| **Responsable de resolución (JD)** | Normalmente el jefe del departamento afectado. Designa al Ejecutor y opina sobre lo ejecutado. |
| **Ejecutor** | Propone acciones y fecha prevista, y las ejecuta. Puede coordinar a terceros. |
| **RSGI** | Responsable del Sistema de Gestión Integrado (es el responsable de Calidad). |

> CLD es el departamento de Calidad. Mantén la sigla tal cual en el código: es
> la que usan los usuarios.

### 1.2 Etapas del flujo (PG09 §5)

1. **Detección** — cualquier persona detecta la MIR.
2. **Registro** — alta en el aplicativo, preferiblemente en **1 día hábil**. La
   descripción relata *qué ha pasado*, sin valoraciones ni propuestas de acción.
   Puede llevar archivos adjuntos. El detector indica si ya está resuelta.
3. **Evaluación y clasificación (CLD)** — el técnico decide:
   - No procede → **se archiva** sin resolución.
   - Mal cumplimentada → **se devuelve al usuario** con comentarios.
   - Correcta → clasifica (origen y tipología) y designa **responsable de
     resolución**.
4. **Propuesta de resolución** — el responsable selecciona **Ejecutor**; el
   Ejecutor propone acciones y **fecha prevista de ejecución**, e incluye el
   **análisis de causas** (5 porqués; nunca una repetición de la descripción).
5. **Ejecución** — aprobada la propuesta por CLD, el Ejecutor ejecuta y
   documenta lo hecho.
6. **Cierre y evaluación (CLD)** — si la valoración es positiva se cierra, y el
   sistema pregunta dos cosas: **¿requiere Comprobación de Eficacia (CE)?** y
   **¿hay más acciones que hacer?** Si no requiere CE, se cierra indicando los
   motivos. Si requiere CE, hay que fijar **fecha de CE** y **en qué sentido**
   se hará.
7. **Comprobación de Eficacia (CE)** — resultado favorable → avanza a
   finalización; desfavorable → **se evalúa** abrir una MIR relacionada (nunca
   automático) y se registra el resultado de esa evaluación.
8. **Finalización** — CLD añade resumen, valoración de avance, valoración de
   coste y palabras clave. La MIR queda **archivada** y consultable.

Bucles del flujograma (Anexo 1) que hay que respetar:

- En "¿está resuelta?" y en "¿algo más que hacer?" el circuito puede volver al
  usuario y **reiniciarse desde el punto 5**, o abrir una **MIR relacionada**.
- Una CE desfavorable puede generar una **MIR relacionada**. Las MIR se enlazan
  entre sí; el modelo de dominio debe soportar esa relación.

### 1.3 Clasificación

Se clasifica por **origen** y por **tipología**. Tipos y subtipos del PG09 §4:

- **Auditoría interna** → subcategorías: Análisis, Formación, Proyecto, Proceso.
- **Auditoría externa** → subtipos: Acreditadora/Certificadora, Empresa.
  Se anota como referencia el código asignado por la entidad auditora.
- **Reclamación** (cliente u otra parte interesada).
- **Interna** (incumplimiento que no afecta al producto/servicio final).
- **Correctiva** (elimina la causa raíz; implantación larga).
- **Preventiva** (problema potencial; implantación corta).
- **Proveedor** — incluye **PMP (Pre-MIR de Proveedor)** para incidencias leves;
  su reiteración puede motivar la apertura de una MIR completa.
- **Trabajo/Producto/Servicio no conforme (TNC)**.
- **Revisión del sistema por la dirección**.
- **Propuesta de mejora**.

### 1.4 Reglas de negocio con efectos en el código

- **TNC**: antes de proponer acciones se exigen cuatro datos: alcance,
  valoración de importancia/gravedad, si se ha avisado a la parte interesada, y
  si se ha interrumpido el trabajo (con fechas de inicio y fin).
- **Reclamación**: obligatorio registrar nombre de persona y empresa
  reclamante. Toda comunicación con el cliente queda registrada. Acuse de recibo
  en **24 h** para reclamaciones formales escritas. La MIR se cierra cuando se
  responde al cliente. Ninguna reclamación queda sin contestación.
- **Validación por etapas**: el aplicativo original "no deja avanzar si falta
  algún tipo de información". Replicar: cada transición valida sus campos
  obligatorios en el dominio, no solo en el formulario.
- **Producto no conforme**: se etiqueta con el registro RVG03.

### 1.5 Avisos automáticos (PG09 §6)

| Disparador | Cuándo | A quién | Repetición | Destinatarios de la repetición |
| --- | --- | --- | --- | --- |
| El JD debe asignar Ejecutor | 3 días tras designarse el JD | JD | Cada 3 días | JD, CLD |
| El Ejecutor debe indicar acciones y fecha | 7 días tras designarse el Ejecutor | Ejecutor | Cada 7 días | Ejecutor, JD, CLD |
| Fin del plazo previsto de ejecución | 15 días **antes** de la fecha prevista | Ejecutor | El día de la fecha prevista, luego cada 7 días | Ejecutor, JD, CLD |
| Comprobación de Eficacia | 15 días **antes** de la fecha prevista de CE | CLD | El día de la fecha prevista, luego cada 7 días | CLD |

> El PG09 menciona "10 tipos/momentos de aviso" pero la tabla solo detalla estos
> cuatro. Ver §11 (dudas abiertas).

### 1.6 Informes (PG09 §8)

Consultas por departamento, tipo y motivo: MIR abiertas/cerradas, tiempo de
resolución, tipo de MIR por departamento y estado actual.

---

## 2. Stack

| Área | Tecnología |
| --- | --- |
| Lenguaje | Python (TODO: fijar versión, p.ej. 3.13) |
| Gestor de paquetes | `uv` (el proyecto usa `[dependency-groups]`) |
| Framework HTTP | FastAPI |
| ORM | SQLAlchemy 2.0, estilo async |
| Driver BD | asyncpg (runtime) / psycopg (herramientas y Alembic) |
| Migraciones | Alembic |
| Configuración | pydantic-settings |
| Almacenamiento documental | SharePoint vía msgraph-sdk + azure-identity |
| Tests | pytest |
| Lint y formato | ruff |
| Tipos | basedpyright |
| Hooks | pre-commit |

No se usa nada que no esté en esta tabla.

---

## 3. Comandos

```bash
# Entorno
uv sync

# Tests
uv run pytest
uv run pytest tests/unit/mir -k "nombre_del_test"

# Lint y formato (obligatorio tras generar o modificar código)
uv run ruff check --fix .
uv run ruff format .

# Tipos (obligatorio tras generar o modificar código)
uv run basedpyright

# Migraciones
uv run alembic revision --autogenerate -m "descripcion"
uv run alembic upgrade head
```

**Definición de "terminado":** `pytest`, `ruff check`, `ruff format` y
`basedpyright` pasan en limpio. No anuncies que has acabado antes de
ejecutarlos.

---

## 4. Arquitectura

Arquitectura **modular**; cada módulo contiene internamente una **Clean
Architecture**.

### 4.1 Módulos

- **`archivos`** — subida y descarga de archivos y su almacenamiento en
  SharePoint (Microsoft Graph). Da servicio a los adjuntos de la MIR
  (descripciones, informes de auditoría, comunicaciones con el cliente).
- **`mir`** — ciclo de vida completo de la MIR según el PG09.

### 4.2 Capas dentro de un módulo

```
src/modules/<modulo>/
├── domain/           # Entidades, value objects, excepciones e interfaces (puertos)
├── application/      # Casos de uso, DTOs
├── infrastructure/   # SQLAlchemy, cliente Graph, implementaciones de puertos
└── api/     # Routers FastAPI, esquemas de request/response
```

> **TODO:** confirmar que estos nombres coinciden con el repositorio real.

### 4.3 Regla de dependencias

Las dependencias apuntan **siempre hacia adentro**:

```
api → application → domain
infrastructure → domain (implementa sus interfaces)
```

- `domain` no importa SQLAlchemy, FastAPI ni msgraph. Solo stdlib y, como mucho,
  pydantic para value objects.
- `application` depende de interfaces de `domain`, nunca de implementaciones.
- `infrastructure` es la única capa que conoce la BD y SharePoint.
- Las entidades de dominio **no** son modelos de SQLAlchemy; se mapean en
  `infrastructure`.

### 4.4 Dónde vive la máquina de estados

Las transiciones entre etapas del PG09 (§1.2) son **reglas de dominio**, no de
presentación. Viven en `mir/domain`. Un caso de uso invoca la transición; la
entidad decide si es legal. Ningún router debe decidir si una MIR puede pasar de
una etapa a otra.

Cada transición valida quién puede dispararla (§1.1) y qué campos exige (§1.4).
Una transición ilegal lanza una excepción de dominio, no un `HTTPException`.

### 4.5 Comunicación entre módulos

Un módulo **nunca** importa el interior de otro.

> **TODO:** confirmar el mecanismo. Propuesta por defecto: `mir/domain` declara
> un puerto (p.ej. `AlmacenDeArchivos`) y `archivos` aporta la implementación,
> inyectada en el arranque.

---

## 5. Estilo de código

- Type hints en **todas** las firmas: parámetros, retorno y atributos de clase.
  Objetivo: `basedpyright` limpio, sin `# type: ignore`.
- Nada de `Any` salvo justificación en comentario.
- Prohibido `# noqa` y `# type: ignore` sin comentario que explique el motivo.
- I/O siempre asíncrono en application, infrastructure y presentation. Nada
  bloqueante dentro del event loop.
- **Estados, tipos y roles se modelan como `Enum` o value objects**, nunca como
  `str` sueltos.
- Busca siempre la solución más simple que funcione. No introduzcas
  abstracciones ni patrones que la tarea no pida.
- **Vocabulario en español, el del PG09**: `Reclamacion`, `Ejecutor`,
  `ComprobacionEficacia`, `AnalisisCausas`, `TrabajoNoConforme`. No traduzcas
  términos de dominio al inglés ni inventes sinónimos. Sin tildes en
  identificadores.

---

## 6. Tests y TDD

**TDD obligatorio para toda funcionalidad nueva**, no solo para módulos nuevos:

1. Escribir el test que falla.
2. Ejecutarlo y comprobar que falla por el motivo esperado.
3. Escribir el mínimo código que lo hace pasar.
4. Refactorizar.

### Organización

```
tests/
├── unit/<modulo>/          # Dominio y casos de uso, sin I/O
└── integration/<modulo>/   # BD de test, routers, adaptadores
```

### Reglas

- Los tests de `domain` y `application` no tocan BD, red ni disco. Puertos
  sustituidos por dobles escritos a mano.
- **Nunca** llamadas reales a SharePoint / Microsoft Graph en tests.
- Integración contra BD de test desechable, nunca la de desarrollo.
- **Toda transición de estado nueva necesita dos tests como mínimo**: el camino
  feliz y el intento ilegal (rol incorrecto o campos obligatorios ausentes).
- Nombres de test que describan el comportamiento, no la función invocada.

> **TODO:** el grupo `dev` no incluye librería para tests async
> (`pytest-asyncio` o `anyio`). Con FastAPI + SQLAlchemy async hará falta.
> Decidir cuál y añadirla siguiendo la regla del §8.

---

## 7. Flujo spec-driven

1. Leer `docs/constitution.md`.
2. Leer el **PG09** (`docs/PG09_Gestión_de_MIR_rev14.pdf`) cuando la tarea toque
   reglas de negocio.
3. Leer la spec activa en `specs/`.

   > **TODO:** definir cómo se identifica la spec activa (convención de nombre,
   > `status:` en front-matter, carpeta `specs/active/`…). Mientras no esté
   > definido, el agente pregunta.

4. Implementar solo lo que la spec describe. Si la spec no cubre algo que
   necesitas, **para y pregunta**; no lo resuelvas por tu cuenta.
5. No modificar archivos de `specs/` salvo petición explícita.

**Si el código y el PG09 se contradicen, no elijas por tu cuenta: repórtalo.**

---

## 8. Cambios que requieren aprobación previa

Antes de hacer cualquiera de estas cosas, **detente y pregunta**. Solo tras
aprobación se implementa, y en el mismo cambio se actualiza la spec.

- Añadir, eliminar o subir de versión mayor una dependencia.
- Cambios de arquitectura: nuevos módulos, nuevas capas, movimiento de
  responsabilidades.
- Cambios en contratos o interfaces públicas: puertos de `domain`, esquemas de
  request/response, rutas HTTP, códigos de estado.
- **Cambios en la máquina de estados de la MIR**: estados nuevos, transiciones
  nuevas, cambios de permisos por rol o de campos obligatorios. Esto es un
  cambio de procedimiento certificado, no una decisión técnica.
- Borrado o renombrado de archivos.
- Migraciones destructivas.

---

## 9. No tocar

- `specs/` (salvo petición explícita) y `docs/PG09*`.
- Migraciones de Alembic ya aplicadas. Si el esquema cambia, migración nueva.
- `.env` y cualquier archivo con credenciales. Las credenciales de Azure y
  SharePoint se leen vía `pydantic-settings`; nunca hardcodeadas ni en logs.
- Archivos generados y `.venv/`.

---

## 10. Trazabilidad y datos personales

El PG09 es un procedimiento sujeto a auditoría (ISO 9001, 14001, 17025, 22000).
Consecuencias directas:

- **Nada se borra.** Archivar y finalizar son estados, no `DELETE`. No añadas
  borrado físico de MIR, acciones ni adjuntos.
- **Todo cambio de estado deja rastro**: quién, cuándo, de qué estado a cuál.
  Esa traza es parte del dominio, no un log de aplicación.
- Las MIR contienen **datos personales de clientes y empleados** (nombre de
  reclamante, empresa, comunicaciones). No los incluyas en logs, mensajes de
  error, fixtures ni datos de prueba. Los tests usan datos ficticios.