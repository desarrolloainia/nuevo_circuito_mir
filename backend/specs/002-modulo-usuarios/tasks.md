---

description: "Task list template for feature implementation"
---

# Tasks: Módulo Usuarios

**Input**: Design documents from `/specs/002-modulo-usuarios/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/usuarios-api.md

**Alcance de esta entrega** (decisión explícita del usuario en `/speckit-tasks`):
solo `domain` + `application` del módulo `usuarios`, con un doble de
repositorio en memoria para los tests. **Fuera de alcance**: `src/shared/`
(database.py, uow.py), persistencia SQLAlchemy real, bootstrap de Alembic y
el router FastAPI (`api/`) descrito en `contracts/usuarios-api.md` — se
implementarán en una tarea posterior.

**Tests**: incluidos y obligatorios (TDD, CLAUDE.md §6 y Constitution
Principio I): mínimo un test de camino feliz y uno de caso ilegal por regla
de negocio.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Módulo: `src/modules/usuarios/{domain,application}/...`
- Tests: `tests/unit/usuarios/...`

**Nota post-implementación**: la convención real del repo (heredada de
`archivos`) coloca cada tipo de dominio en su propia subcarpeta —
`domain/Entities/usuario.py`, `domain/Enum/rol.py`,
`domain/Exceptions/excepciones.py` — e importa siempre como
`modules.usuarios...` (sin prefijo `src.`, que requiere `src/` en el
`pythonpath`, añadido en `pyproject.toml` junto a `.`). Los ficheros de
código y test se ajustaron a esa convención; las rutas planas indicadas en
las tareas de abajo (`domain/usuario.py`, `domain/rol.py`,
`domain/excepciones.py`) deben leerse como sus equivalentes reales.

---

## Phase 1: Setup

**Purpose**: Esqueleto de paquete del módulo (no existe todavía ni `tests/`
en el repo)

- [x] T001 Crear esqueleto de paquete `src/modules/usuarios/` con
  `src/modules/usuarios/__init__.py`, `src/modules/usuarios/domain/__init__.py`,
  `src/modules/usuarios/domain/repository/__init__.py`,
  `src/modules/usuarios/application/__init__.py`,
  `src/modules/usuarios/application/uses_cases/__init__.py`
- [x] T002 [P] Crear `tests/unit/usuarios/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entidad `Usuario`, value objects, excepciones y el puerto de
repositorio que todas las historias de usuario necesitan

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Crear `Rol` (Enum) en `src/modules/usuarios/domain/rol.py` con
  el catálogo cerrado del PG09 §1.1: `DETECTOR`, `JEFE_CLD`, `TECNICO_CLD`,
  `RESPONSABLE_RESOLUCION`, `EJECUTOR`, `RSGI`
- [x] T004 [P] Test: `Correo` con formato inválido (sin `@`, dominio vacío,
  etc.; regex de referencia `^[^@\s]+@[^@\s]+\.[^@\s]+$`) lanza
  `FormatoCorreoInvalidoError` en `tests/unit/usuarios/test_usuario_entidad.py`
- [x] T005 [P] Test: `Departamento` vacío o solo espacios (tras `strip()`)
  lanza `DatoObligatorioFaltanteError("departamento")` en
  `tests/unit/usuarios/test_usuario_entidad.py`
- [x] T006 Crear `src/modules/usuarios/domain/excepciones.py` con
  `CorreoYaRegistradoError`, `RolInvalidoError`, `FormatoCorreoInvalidoError`,
  `DatoObligatorioFaltanteError`, `UsuarioNoEncontradoError`
- [x] T007 Implementar value objects `Correo` y `Departamento` (dataclass
  `frozen=True`, validación en `__post_init__`) en
  `src/modules/usuarios/domain/usuario.py` — debe hacer pasar T004 y T005
- [x] T008 [P] Test: `Usuario` no puede construirse si falta correo, rol o
  departamento válidos en `tests/unit/usuarios/test_usuario_entidad.py`
- [x] T009 [P] Test: `Usuario.dar_de_baja()` fija `activo=False` y
  `dado_de_baja_en` (no `None`); llamarlo dos veces es idempotente, no lanza
  error, en `tests/unit/usuarios/test_usuario_entidad.py`
- [x] T010 Implementar entidad `Usuario` (dataclass) en
  `src/modules/usuarios/domain/usuario.py`: `id: UUID` (`default_factory=uuid4`,
  clave técnica), `correo: Correo` (inmutable tras el alta), `rol: Rol`,
  `departamento: Departamento`, `activo: bool = True`,
  `creado_en: datetime` (UTC, `default_factory=lambda: datetime.now(UTC)`),
  `dado_de_baja_en: datetime | None = None`; método `dar_de_baja()` que fija
  `activo=False` y `dado_de_baja_en=datetime.now(UTC)` solo si estaba activo
  (no-op idempotente si ya estaba inactivo) — debe hacer pasar T008 y T009
- [x] T011 [P] Crear `Protocol UsuarioRepository` en
  `src/modules/usuarios/domain/repository/usuario_repository.py` con métodos
  `async def guardar(self, usuario: Usuario) -> None`,
  `async def obtener_por_correo(self, correo: str) -> Usuario | None`,
  `async def listar_activos(self) -> list[Usuario]`,
  `async def actualizar(self, usuario: Usuario) -> None`
- [x] T012 Crear doble de test `UsuarioRepositoryEnMemoria` (implementa
  `UsuarioRepository` a mano con un `dict[str, Usuario]` indexado por correo,
  sin mocks ni librerías — Constitution Principio I) en
  `tests/unit/usuarios/dobles.py`

**Checkpoint**: dominio y puerto de repositorio listos — las historias de
usuario pueden empezar

---

## Phase 3: User Story 1 - Alta de un usuario (Priority: P1) 🎯 MVP

**Goal**: registrar un usuario con correo, rol y departamento válidos,
rechazando correos duplicados o datos obligatorios ausentes (FR-001 a
FR-005)

**Independent Test**: dar de alta un usuario con correo/rol/departamento
válidos y comprobar que queda en el repositorio (obtenible vía
`repo.obtener_por_correo`), sin depender de los casos de uso de consulta

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Test: `registrar_usuario` con correo, rol y
  departamento válidos guarda el usuario, obtenible vía
  `repo.obtener_por_correo` en `tests/unit/usuarios/test_registrar_usuario.py`
- [x] T014 [P] [US1] Test: `registrar_usuario` con un correo ya registrado
  lanza `CorreoYaRegistradoError` en
  `tests/unit/usuarios/test_registrar_usuario.py`
- [x] T015 [P] [US1] Test: `registrar_usuario` con correo, rol o
  departamento ausente (cadena vacía) lanza `DatoObligatorioFaltanteError`
  en `tests/unit/usuarios/test_registrar_usuario.py`
- [x] T016 [P] [US1] Test: `registrar_usuario` con correo de formato
  inválido lanza `FormatoCorreoInvalidoError` en
  `tests/unit/usuarios/test_registrar_usuario.py`
- [x] T017 [P] [US1] Test: `registrar_usuario` con un rol fuera del catálogo
  PG09 lanza `RolInvalidoError` en
  `tests/unit/usuarios/test_registrar_usuario.py`

### Implementation for User Story 1

- [x] T018 [US1] Implementar
  `async def registrar_usuario(repo: UsuarioRepository, correo: str, rol: str, departamento: str) -> Usuario`
  en `src/modules/usuarios/application/uses_cases/registrar_usuario.py`:
  valida que `rol` pertenece al Enum `Rol` (si no, `RolInvalidoError`),
  comprueba que `repo.obtener_por_correo(correo)` es `None` (si no,
  `CorreoYaRegistradoError`), construye `Usuario` (propagando
  `FormatoCorreoInvalidoError`/`DatoObligatorioFaltanteError` de los value
  objects) y llama a `repo.guardar(usuario)` — debe hacer pasar T013-T017

**Checkpoint**: At this point, User Story 1 should be fully functional and
testable independently

---

## Phase 4: User Story 2 - Consulta de usuarios (Priority: P1)

**Goal**: consultar un usuario por correo o listar los usuarios activos
(FR-006, FR-007)

**Independent Test**: dar de alta uno o varios usuarios (vía el doble de
repositorio) y comprobar que se pueden consultar individualmente y listar

### Tests for User Story 2 ⚠️

- [x] T019 [P] [US2] Test: `consultar_usuario` devuelve correo, rol y
  departamento de un usuario existente en
  `tests/unit/usuarios/test_consultar_usuario.py`
- [x] T020 [P] [US2] Test: `consultar_usuario` con un correo que no
  corresponde a ningún usuario lanza `UsuarioNoEncontradoError` en
  `tests/unit/usuarios/test_consultar_usuario.py`
- [x] T021 [P] [US2] Test: `listar_usuarios` devuelve únicamente los
  usuarios activos (excluye los dados de baja) en
  `tests/unit/usuarios/test_listar_usuarios.py`

### Implementation for User Story 2

- [x] T022 [US2] Implementar
  `async def consultar_usuario(repo: UsuarioRepository, correo: str) -> Usuario`
  en `src/modules/usuarios/application/uses_cases/consultar_usuario.py`:
  lanza `UsuarioNoEncontradoError` si `repo.obtener_por_correo` devuelve
  `None` — debe hacer pasar T019-T020
- [x] T023 [US2] Implementar
  `async def listar_usuarios(repo: UsuarioRepository) -> list[Usuario]` en
  `src/modules/usuarios/application/uses_cases/listar_usuarios.py`
  delegando en `repo.listar_activos()` — debe hacer pasar T021

**Checkpoint**: alta + consulta cubren el MVP completo (US1 + US2 = P1)

---

## Phase 5: User Story 3 - Actualización y baja de un usuario (Priority: P2)

**Goal**: actualizar rol/departamento de un usuario activo y darlo de baja
lógicamente, sin eliminar el registro (FR-008, FR-009, FR-011)

**Independent Test**: modificar rol/departamento de un usuario existente y
comprobar el cambio; dar de baja un usuario y comprobar que desaparece del
listado de activos pero sigue siendo consultable, y que ya no admite
actualizaciones

### Tests for User Story 3 ⚠️

- [x] T024 [P] [US3] Test: `actualizar_usuario` sobre un usuario activo
  cambia su rol y/o departamento en
  `tests/unit/usuarios/test_actualizar_usuario.py`
- [x] T025 [P] [US3] Test: `actualizar_usuario` sobre un correo inexistente
  lanza `UsuarioNoEncontradoError` en
  `tests/unit/usuarios/test_actualizar_usuario.py`
- [x] T026 [P] [US3] Test: `actualizar_usuario` sobre un usuario ya dado de
  baja lanza `UsuarioInactivoError` en
  `tests/unit/usuarios/test_actualizar_usuario.py`
- [x] T027 [P] [US3] Test: `dar_baja_usuario` marca el usuario como inactivo
  y deja de aparecer en `listar_usuarios`, pero sigue siendo consultable por
  `consultar_usuario` (con `activo=False`) en
  `tests/unit/usuarios/test_dar_baja_usuario.py`
- [x] T028 [P] [US3] Test: `dar_baja_usuario` sobre un correo inexistente
  lanza `UsuarioNoEncontradoError` en
  `tests/unit/usuarios/test_dar_baja_usuario.py`
- [x] T029 [P] [US3] Test: `dar_baja_usuario` es idempotente (repetirla
  sobre un usuario ya inactivo no lanza error) en
  `tests/unit/usuarios/test_dar_baja_usuario.py`

### Implementation for User Story 3

- [x] T030 [US3] Añadir `UsuarioInactivoError` a
  `src/modules/usuarios/domain/excepciones.py`
- [x] T031 [US3] Implementar método `Usuario.actualizar(rol: Rol | None = None, departamento: Departamento | None = None) -> None`
  en `src/modules/usuarios/domain/usuario.py`: lanza `UsuarioInactivoError`
  si `self.activo` es `False`; si no, aplica los campos presentes — debe
  contribuir a hacer pasar T024 y T026
- [x] T032 [US3] Implementar
  `async def actualizar_usuario(repo: UsuarioRepository, correo: str, rol: str | None = None, departamento: str | None = None) -> Usuario`
  en `src/modules/usuarios/application/uses_cases/actualizar_usuario.py`:
  lanza `UsuarioNoEncontradoError` si no existe, valida `rol` contra el
  catálogo si se proporciona (`RolInvalidoError`), llama a
  `usuario.actualizar(...)` y `repo.actualizar(usuario)` — debe hacer pasar
  T024-T026
- [x] T033 [US3] Implementar
  `async def dar_baja_usuario(repo: UsuarioRepository, correo: str) -> None`
  en `src/modules/usuarios/application/uses_cases/dar_baja_usuario.py`:
  lanza `UsuarioNoEncontradoError` si no existe; si no, llama a
  `usuario.dar_de_baja()` y `repo.actualizar(usuario)` — debe hacer pasar
  T027-T029

**Checkpoint**: ciclo completo alta/consulta/actualización/baja cubierto en
`domain`+`application` (sin persistencia real ni API, fuera de alcance de
esta entrega)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: cumplir la Definición de "terminado" de CLAUDE.md §3 para el
módulo `usuarios`

- [x] T034 [P] `uv run ruff check --fix .` y `uv run ruff format .` sobre
  `src/modules/usuarios/` y `tests/unit/usuarios/`
- [x] T035 [P] `uv run basedpyright` limpio sobre
  `src/modules/usuarios/domain/` y `src/modules/usuarios/application/`
- [x] T036 `uv run pytest tests/unit/usuarios -v` — todos los tests en verde

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias, empieza de inmediato
- **Foundational (Phase 2)**: depende de Setup — bloquea todas las historias
  de usuario
- **User Stories (Phase 3-5)**: dependen de Foundational; US1 y US2 son
  ambas P1 y pueden avanzar en paralelo con distintos ficheros de test; US3
  (P2) añade `UsuarioInactivoError` y el método `Usuario.actualizar`, por lo
  que conviene completarla después de US1
- **Polish (Phase 6)**: depende de que las historias que se quieran entregar
  estén completas

### User Story Dependencies

- **US1 (P1)**: solo depende de Foundational
- **US2 (P1)**: solo depende de Foundational (usa el mismo doble de
  repositorio, no depende de que exista código de US1)
- **US3 (P2)**: depende de Foundational; reutiliza `UsuarioNoEncontradoError`
  (T006) y añade `UsuarioInactivoError` (T030)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Casos de uso después de que existan las excepciones y la entidad
  (Foundational)
- Historia completa antes de pasar a la siguiente en orden de prioridad

### Parallel Opportunities

- T003, T004, T005 (Foundational) en paralelo
- T008, T009 (Foundational) en paralelo, después de T006/T007
- T011 en paralelo con los tests anteriores
- T013-T017 (tests US1) en paralelo entre sí
- T019-T021 (tests US2) en paralelo entre sí
- T024-T029 (tests US3) en paralelo entre sí
- T034 y T035 (Polish) en paralelo

---

## Parallel Example: User Story 1

```bash
# Lanzar todos los tests de US1 en paralelo:
Task: "Test alta válida en tests/unit/usuarios/test_registrar_usuario.py"
Task: "Test correo duplicado en tests/unit/usuarios/test_registrar_usuario.py"
Task: "Test dato obligatorio ausente en tests/unit/usuarios/test_registrar_usuario.py"
Task: "Test correo con formato inválido en tests/unit/usuarios/test_registrar_usuario.py"
Task: "Test rol fuera de catálogo en tests/unit/usuarios/test_registrar_usuario.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2, ambas P1)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICAL - bloquea todas las historias)
3. Completar Phase 3: User Story 1 (alta)
4. Completar Phase 4: User Story 2 (consulta)
5. **STOP and VALIDATE**: `uv run pytest tests/unit/usuarios -v`

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 (alta) → probar de forma aislada
3. US2 (consulta) → probar de forma aislada → MVP completo (P1+P1)
4. US3 (actualización y baja, P2) → probar de forma aislada
5. Polish (lint, tipos, tests) → definición de "terminado"

---

## Notes

- [P] tasks = distintos ficheros o casos independientes en el mismo fichero,
  sin dependencias entre sí
- [Story] label mapea la tarea a su historia de usuario
- No se implementa persistencia real, API ni Alembic en esta entrega
  (decisión explícita del usuario) — ver `plan.md` para el alcance completo
  pendiente
- Cada regla de negocio nueva lleva mínimo dos tests: camino feliz y caso
  ilegal (rol incorrecto o dato obligatorio ausente), conforme a CLAUDE.md §6
