# Implementation Plan: Módulo Usuarios

**Branch**: `002-modulo-usuarios` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-modulo-usuarios/spec.md`

## Summary

Crear el módulo `usuarios`: alta, consulta, actualización y baja lógica de un
`Usuario` con tres atributos (correo, rol, departamento), sin autenticación.
El rol es un catálogo cerrado (los roles del PG09); el departamento es texto
libre; el correo es el identificador único. Sigue la Clean Architecture
modular ya establecida por el módulo `archivos` (`domain` →
`application` → `infrastructure`/`api`).

**Hallazgo relevante para el alcance técnico**: `archivos` ya referencia
`shared.database` (clase `Base`, engine, sesión async) y `shared.uow`
(`UnitOfWork`), pero `src/shared/` está vacío — esa infraestructura compartida
nunca se implementó, así que ni `archivos` es ejecutable hoy. Tampoco existe
bootstrap de FastAPI (`main.py` es un stub de PyCharm), ni configuración de
Alembic, ni carpeta `tests/`. Este plan asume que `usuarios` necesita crear
esa infraestructura compartida mínima (no es una capa ni un módulo nuevo: es
completar lo que `archivos` ya da por hecho), porque sin ella no hay manera de
persistir ni exponer nada. Se señala explícitamente por si se prefiere
acotar esta primera iteración a `domain`+`application` (sin persistencia real
ni API) — ver "Complexity Tracking".

## Technical Context

**Language/Version**: Python >=3.14 (fijado en `pyproject.toml`)

**Primary Dependencies**: FastAPI (`fastapi[standard]`), SQLAlchemy 2.0 async,
pydantic-settings. Sin dependencias nuevas: la validación de correo se hace
con `re` de stdlib (evita añadir `email-validator`, que exigiría aprobación
previa por AGENTS.md §8).

**Storage**: PostgreSQL vía `asyncpg` en runtime; `psycopg` para Alembic,
igual que documenta CLAUDE.md.

**Testing**: `pytest`. Sin `pytest-asyncio`/`anyio` (no están instalados y
añadirlos requiere aprobación — AGENTS.md §8). Los tests async de
`domain`/`application` envuelven las llamadas con `asyncio.run(...)`, patrón
estándar de stdlib, suficiente para dobles de puertos escritos a mano.

**Target Platform**: Servicio backend Linux (contenedor/uvicorn), igual que el
resto del backend.

**Project Type**: Módulo dentro de un backend modular monolítico (FastAPI +
Clean Architecture por módulo), no un proyecto nuevo.

**Performance Goals**: Ninguno específico más allá de SC-001 (alta en menos
de 1 minuto humano); es un CRUD simple sin carga previsible relevante.

**Constraints**: `domain` no importa SQLAlchemy, FastAPI ni msgraph
(Principio IV). Nada se borra físicamente (Principio V) — la baja es un
cambio de estado (`activo=False`), no un `DELETE` de fila.

**Scale/Scope**: Decenas de usuarios internos de la organización (empleados
de AINIA que participan en el PG09), no miles.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento |
|---|---|
| I. Test-First | Se seguirá TDD: cada caso de uso y cada regla de la entidad `Usuario` (correo duplicado, rol inválido, campos obligatorios, baja de inactivo) tiene su test antes del código. Mínimo dos tests por regla (camino feliz + caso ilegal). |
| II. Type Hints Estrictos | `Rol` como `Enum`; `Correo` y `Departamento` como value objects (no `str` suelto); sin `Any`. |
| III. Calidad sobre Cantidad | Sin capas ni patrones extra: un Protocol de repositorio, casos de uso como funciones, sin generic repository ni CQRS. |
| IV. El Dominio es Sagrado | `domain/usuario.py`, `domain/rol.py`, `domain/excepciones.py` no importan SQLAlchemy/FastAPI. Las reglas (correo único, rol válido, baja lógica) viven en la entidad/casos de uso de `domain`/`application`, no en el router. |
| V. Trazabilidad Total | Baja = `activo=False` con `dado_de_baja_en: datetime`, nunca `DELETE`. Sin datos personales en logs/fixtures (los tests usan correos ficticios `@ejemplo.test`). |
| Clean Architecture modular | Nueva carpeta `src/modules/usuarios/` con `domain/application/infrastructure/api`, sin importar el interior de `mir` ni `archivos`. |

**Resultado**: PASA, sujeto a la nota de "shared/" del Summary (no es una
violación de arquitectura — es completar infraestructura ya prevista por
`archivos` — pero se documenta en Complexity Tracking por transparencia).

## Project Structure

### Documentation (this feature)

```text
specs/002-modulo-usuarios/
├── plan.md              # Este fichero
├── research.md          # Fase 0
├── data-model.md         # Fase 1
├── quickstart.md         # Fase 1
├── contracts/
│   └── usuarios-api.md   # Fase 1
└── tasks.md              # Fase 2 (/speckit-tasks, no se crea aquí)
```

### Source Code (repository root)

```text
src/
├── shared/                          # Infraestructura común (hoy vacía, se completa aquí)
│   ├── database.py                  # Base declarativa, engine, async_sessionmaker
│   └── uow.py                       # UnitOfWork (mismo contrato que ya usa archivos)
│
└── modules/
    └── usuarios/
        ├── domain/
        │   ├── rol.py                # Enum Rol (roles del PG09)
        │   ├── usuario.py            # Entidad Usuario (dataclass) + value objects Correo/Departamento
        │   ├── excepciones.py        # CorreoYaRegistradoError, UsuarioNoEncontradoError, RolInvalidoError, DatoObligatorioFaltanteError
        │   └── repository/
        │       └── usuario_repository.py   # Protocol UsuarioRepository
        ├── application/
        │   ├── dto.py                 # DTOs de entrada/salida de los casos de uso
        │   └── uses_cases/
        │       ├── registrar_usuario.py
        │       ├── consultar_usuario.py
        │       ├── listar_usuarios.py
        │       ├── actualizar_usuario.py
        │       └── dar_baja_usuario.py
        ├── infrastructure/
        │   └── db/
        │       ├── entities/usuario.py            # Modelo SQLAlchemy (tabla `usuarios`)
        │       └── persistence/usuario_repository.py  # UsuarioRepositorySqlAlchemy
        └── api/
            ├── dto.py                 # Esquemas pydantic de request/response
            └── router.py              # APIRouter(prefix="/usuarios")

alembic/                              # Bootstrap de migraciones (no existe hoy)
├── env.py
└── versions/
    └── <rev>_create_usuarios_table.py

tests/
├── unit/usuarios/
│   ├── test_usuario_entidad.py
│   ├── test_registrar_usuario.py
│   ├── test_actualizar_usuario.py
│   └── test_dar_baja_usuario.py
└── integration/usuarios/
    └── test_usuario_router.py
```

**Structure Decision**: Se añade el módulo `usuarios` con la misma forma que
`archivos` (domain/application/infrastructure/api). Se crea `src/shared/`
porque `archivos` ya depende de ella sin que exista; construirla aquí no es
una capa nueva, es completar la infraestructura de persistencia común que el
propio código existente da por hecha. Se añade `alembic/` en la raíz por ser
la herramienta de migraciones ya elegida en CLAUDE.md, y `tests/` porque hoy
no existe ninguna carpeta de tests en el repo.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| Crear `src/shared/database.py` y `src/shared/uow.py` desde cero | Sin ellos no hay forma de persistir `Usuario` (ni de que `archivos` funcione); son infraestructura, no dominio ni módulo nuevo | Omitirlos deja el módulo sin persistencia real: solo se podrían entregar `domain`+`application` con dobles en memoria, sin cumplir FR-001..FR-009 de forma end-to-end. Se documenta para que el usuario confirme si quiere esta infraestructura ahora o prefiere acotar la primera entrega a dominio+casos de uso sin API/BD real. |
| Bootstrap de Alembic (no existe en el repo) | CLAUDE.md exige migraciones vía Alembic para persistir el esquema de `usuarios` | Sin migraciones, la tabla `usuarios` no puede crearse de forma reproducible/auditable |

**Resuelto (2026-09-14)**: el usuario confirmó que quiere la persistencia
real ahora. `src/shared/database.py` y `src/shared/uow.py` ya existían
(creados en algún momento para `archivos`, sin commitear a este plan) y se
reutilizan tal cual. Se implementó `infrastructure` de `usuarios`
(`UsuarioORM`, `UsuarioRepositorySqlAlchemy`) y se corrigió el bootstrap de
Alembic, que existía como scaffold sin terminar (`target_metadata = None`,
driver `asyncpg` incompatible con el `engine_from_config` síncrono que usa
`env.py`). Ver `tasks.md` Fase 7 para el detalle y una limitación pendiente:
la migración inicial se escribió a mano (sin `--autogenerate`) por no haber
Postgres disponible en el entorno de desarrollo para generarla/ejecutarla; el
metadata de `archivos` (`DocumentoORM`) tampoco está registrado en
`env.py` — preexistente, fuera del alcance de este cambio.

**Resuelto (2026-09-14, continuación)**: la API/router de `usuarios` ya no
está fuera de alcance — el usuario pidió los DTO y después corrigió un
router que había empezado a escribir. Implementados `api/dto.py` y
`api/router.py` con los 5 endpoints de `contracts/usuarios-api.md`. Ver
`tasks.md` Fase 8. Queda una desviación del Principio I (Test-First) sin
resolver: no hay test de router (`tests/integration/usuarios/
test_usuario_router.py`, previsto más abajo en este mismo documento) porque
`httpx` no está instalado y añadirlo requiere aprobación previa — T046 en
`tasks.md`. Tampoco existe `main.py`/bootstrap de FastAPI real: el router no
está montado en ninguna app.
