<!--
Sync Impact Report
Version change: (sin ratificar, plantilla vacía) → 1.0.0
Ratificación inicial. No había constitución formal previa: el fichero solo
contenía la plantilla con placeholders sin rellenar. Sin embargo, cinco de
estos seis principios (I-V) ya se usaban de facto como tabla de verificación
en specs/002-modulo-usuarios/plan.md ("Constitution Check") y como reglas
operativas en CLAUDE.md; esta versión los formaliza como fuente de verdad
única, añade el principio VI (arquitectura modular por capas, mencionado en
plan.md sin numerar) y resuelve el resto de la plantilla.

Principios: (nuevos, plantilla → título real)
  - [PRINCIPLE_1_NAME] → I. Test-First (TDD, no negociable)
  - [PRINCIPLE_2_NAME] → II. Type Hints Estrictos
  - [PRINCIPLE_3_NAME] → III. Calidad sobre Cantidad (YAGNI)
  - [PRINCIPLE_4_NAME] → IV. El Dominio es Sagrado
  - [PRINCIPLE_5_NAME] → V. Trazabilidad Total
  - (nuevo) → VI. Arquitectura Modular por Capas

Secciones añadidas:
  - Stack y Restricciones Técnicas (antes [SECTION_2_NAME])
  - Flujo de Desarrollo y Cambios que Requieren Aprobación (antes [SECTION_3_NAME])
  - Governance (reglas de enmienda, versionado, cumplimiento)

Secciones eliminadas: ninguna (era la plantilla vacía).

Deferred / TODO:
  - RATIFICATION_DATE fijada a 2026-09-14 (fecha de esta ratificación formal),
    no a la fecha en que el equipo empezó a aplicar estos principios de
    facto, que no está documentada. Si se recupera esa fecha, corregir aquí.

Plantillas dependientes a revisar tras esta ratificación (no modificadas por
este comando, según el Scope Guard):
  - .specify/templates/plan-template.md (Constitution Check) — ya usa los
    nombres I-V; verificar que VI quede reflejado.
  - .specify/templates/tasks-template.md, spec-template.md — sin referencias
    directas a nombres de principios detectadas; sin acción requerida.
-->

# Circuito MIR Backend Constitution

Backend Python que implementa el procedimiento PG09 de AINIA (gestión de
Mejoras, Incidencias y Reclamaciones). El PG09 es la fuente de verdad del
dominio; esta constitución es la fuente de verdad del *cómo* se construye el
software que lo implementa. Ver `CLAUDE.md` para el detalle operativo del
dominio, comandos y convenciones — esta constitución fija los principios que
ese documento desarrolla y que ningún cambio de código puede contradecir sin
pasar antes por una enmienda (ver Governance).

## Core Principles

### I. Test-First (TDD, no negociable)

Toda funcionalidad nueva, no solo módulos nuevos, sigue TDD: escribir el test
que falla, ejecutarlo y confirmar que falla por el motivo esperado, escribir
el mínimo código que lo hace pasar, refactorizar. Toda transición de estado
nueva o regla de negocio nueva requiere como mínimo dos tests: el camino
feliz y el intento ilegal (rol incorrecto, campo obligatorio ausente, estado
incompatible). Los tests de `domain` y `application` no tocan BD, red ni
disco — los puertos se sustituyen por dobles escritos a mano, nunca mocks de
librería. Nunca hay llamadas reales a servicios externos (SharePoint/
Microsoft Graph, base de datos de desarrollo) en un test.

**Rationale**: el PG09 es un procedimiento auditado (ISO 9001/14001/17025/
22000); una regresión silenciosa en una transición de estado no es un bug de
producto, es un incumplimiento de procedimiento certificado.

### II. Type Hints Estrictos

Type hints en todas las firmas: parámetros, retorno y atributos de clase.
`basedpyright` debe quedar limpio, sin `# type: ignore`. Nada de `Any` salvo
justificación explícita en comentario. Prohibido `# noqa` y `# type: ignore`
sin comentario que explique el motivo. Estados, tipos y roles se modelan
como `Enum` o value objects, nunca como `str` sueltos.

**Rationale**: el dominio (roles, tipologías de MIR, estados del flujo) es un
catálogo cerrado definido por el PG09; un `str` suelto permite valores que el
procedimiento no contempla y que ningún test detecta hasta producción.

### III. Calidad sobre Cantidad (YAGNI)

Se busca siempre la solución más simple que funcione. No se introducen
abstracciones, patrones ni capas que la tarea no pida: sin interfaces con una
sola implementación, sin factorías para un único producto, sin
configurabilidad para un valor que nunca cambia. No se diseña para
requisitos hipotéticos futuros. Ningún cambio de arquitectura, dependencia
nueva o versión mayor de una dependencia existente se introduce sin
aprobación previa del usuario (ver "Cambios que Requieren Aprobación
Previa").

**Rationale**: cada capa y cada abstracción es superficie que alguien debe
entender bajo presión de auditoría o incidencia; la complejidad no
justificada por el PG09 es deuda, no diseño.

### IV. El Dominio es Sagrado

`domain` no importa SQLAlchemy, FastAPI, msgraph ni ningún framework —
como mucho stdlib y pydantic para value objects. `application` depende de
interfaces (`Protocol`) de `domain`, nunca de implementaciones concretas.
`infrastructure` es la única capa que conoce la base de datos y SharePoint.
Las máquinas de estado del PG09 (transiciones entre etapas, quién puede
dispararlas, qué campos exige cada una) son reglas de dominio: viven en
`domain`, nunca en un router. Una transición ilegal lanza una excepción de
dominio, no un `HTTPException`.

**Rationale**: el dominio (PG09) cambia por decisión de Calidad, no por
decisión técnica; si depende de FastAPI o SQLAlchemy, un cambio de framework
obliga a reescribir reglas de negocio que no tenían por qué moverse.

### V. Trazabilidad Total

Nada se borra físicamente. Archivar y finalizar son estados, no `DELETE`; la
baja de un usuario, el cierre de una MIR o la eliminación de un adjunto son
cambios de estado reversibles y consultables, nunca filas eliminadas. Todo
cambio de estado relevante deja rastro de quién, cuándo y de qué estado a
cuál — esa traza es dominio, no un log de aplicación incidental. Las MIR y
otros registros contienen datos personales de clientes y empleados (nombre
de reclamante, empresa, comunicaciones): nunca en logs, mensajes de error,
fixtures ni datos de prueba. Los tests usan datos ficticios.

**Rationale**: el PG09 exige historial completo para auditorías externas
(acreditadora/certificadora); un borrado físico o una traza incompleta
invalida la conformidad del procedimiento, no solo el dato.

### VI. Arquitectura Modular por Capas

El backend es una arquitectura modular; cada módulo (`mir`, `usuarios`,
`archivos`, ...) contiene internamente una Clean Architecture propia:
`domain → application → infrastructure/api`, dependencias siempre hacia
adentro. Un módulo nunca importa el interior de otro módulo — la
comunicación entre módulos pasa por un puerto declarado en `domain` e
implementado/inyectado desde fuera. Nuevos módulos, nuevas capas o cambios en
contratos públicos (rutas HTTP, esquemas de request/response, puertos de
`domain`) requieren aprobación previa del usuario y, en el mismo cambio,
actualización de la spec correspondiente.

**Rationale**: el sistema crecerá módulo a módulo según el PG09 lo requiera
(usuarios, MIR, archivos, informes...); sin este límite de importación, un
atajo entre módulos hoy se convierte en un acoplamiento imposible de separar
mañana.

## Stack y Restricciones Técnicas

Lenguaje Python ≥3.14 gestionado con `uv`. Framework HTTP FastAPI; ORM
SQLAlchemy 2.0 estilo async (`asyncpg` en runtime, `psycopg` para
herramientas y Alembic); migraciones con Alembic; configuración vía
`pydantic-settings`; almacenamiento documental en SharePoint vía
`msgraph-sdk` + `azure-identity`; tests con `pytest`; lint y formato con
`ruff`; tipos con `basedpyright`; hooks con `pre-commit`. No se usa nada que
no esté en este stack. Añadir, eliminar o subir de versión mayor una
dependencia requiere aprobación previa del usuario.

I/O siempre asíncrono en `application`, `infrastructure` y presentación —
nada bloqueante dentro del event loop. Vocabulario de dominio en español, el
del PG09 (`Reclamacion`, `Ejecutor`, `ComprobacionEficacia`,
`AnalisisCausas`, `TrabajoNoConforme`...): no se traduce al inglés ni se
inventan sinónimos; identificadores sin tildes. `.env` y cualquier fichero
con credenciales nunca se hardcodean, se commitean ni aparecen en logs; las
credenciales de Azure y SharePoint se leen vía `pydantic-settings`.

## Flujo de Desarrollo y Cambios que Requieren Aprobación Previa

Flujo spec-driven: leer esta constitución, leer el PG09
(`docs/PG09_Gestión_de_MIR_rev14.pdf`) cuando la tarea toque reglas de
negocio, leer la spec activa en `specs/`, implementar solo lo que la spec
describe. Si la spec no cubre algo necesario, se para y se pregunta — no se
resuelve por cuenta propia. Si el código y el PG09 se contradicen, se
reporta; no se elige por cuenta propia. No se modifican archivos de
`specs/` salvo petición explícita, ni `docs/PG09*`, ni migraciones de
Alembic ya aplicadas (el esquema cambia con una migración nueva).

**Definición de "terminado"**: `pytest`, `ruff check`, `ruff format` y
`basedpyright` pasan en limpio antes de anunciar cualquier tarea como
completada.

**Requieren aprobación previa del usuario** (y, en el mismo cambio,
actualización de la spec): añadir/eliminar/subir de versión mayor una
dependencia; cambios de arquitectura (nuevos módulos, nuevas capas, mover
responsabilidades entre capas); cambios en contratos públicos (puertos de
`domain`, esquemas de request/response, rutas HTTP, códigos de estado);
cambios en la máquina de estados de cualquier flujo del PG09 (estados
nuevos, transiciones nuevas, permisos por rol, campos obligatorios) por
tratarse de un cambio de procedimiento certificado, no una decisión técnica;
borrado o renombrado de archivos; migraciones destructivas.

## Governance

Esta constitución prevalece sobre cualquier otra guía o convención informal
del repositorio, incluido `CLAUDE.md`: si entran en conflicto, se reporta la
contradicción en lugar de resolverla por cuenta propia, y `CLAUDE.md` se
corrige para alinearse con esta constitución en la misma enmienda.

**Enmiendas**: cualquier cambio a esta constitución se hace en un único
commit que actualiza este fichero, incluye un Sync Impact Report en el
comentario HTML superior con el detalle del cambio, y revisa si
`.specify/templates/` u otros artefactos dependientes necesitan
actualizarse en consecuencia (sin modificarlos automáticamente — eso se hace
en un cambio aparte).

**Versionado semántico** de esta constitución:
- MAJOR: eliminación o redefinición incompatible de un principio existente.
- MINOR: principio nuevo añadido, o ampliación material de una guía
  existente.
- PATCH: aclaraciones, correcciones de redacción, refinamientos no
  semánticos.

**Cumplimiento**: toda tarea de implementación (`/speckit-implement` u
equivalente) valida contra estos principios antes de reportarse como
completada; las secciones "Constitution Check" de los planes de
`specs/*/plan.md` son la evidencia de esa validación, no un trámite.
Cualquier violación debe justificarse explícitamente en la sección
"Complexity Tracking" del plan correspondiente o resolverse antes de
implementar.

**Version**: 1.0.0 | **Ratified**: 2026-09-14 | **Last Amended**: 2026-09-14
