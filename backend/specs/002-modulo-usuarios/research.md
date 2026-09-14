# Research: Módulo Usuarios

## 1. Validación de correo sin dependencias nuevas

**Decision**: Value object `Correo` (dataclass `frozen=True`) que valida el
formato con una expresión regular simple de `re` (stdlib) en `__post_init__`,
lanzando `FormatoCorreoInvalidoError` si no matchea.

**Rationale**: `pydantic.EmailStr` requiere el paquete extra
`email-validator`, no instalado. Añadirlo requiere aprobación previa
(AGENTS.md §8: "Añadir... una dependencia"). Una regex básica
(`^[^@\s]+@[^@\s]+\.[^@\s]+$`) cubre el caso de negocio (rechazar formatos
obviamente inválidos) sin sobre-ingeniería — no se necesita validación RFC
5322 completa para este dominio interno.

**Alternatives considered**: `email-validator` (rechazado: dependencia
nueva, requiere aprobación); regex exhaustiva RFC 5322 (rechazada: complejidad
innecesaria para el caso de uso).

## 2. Catálogo de roles

**Decision**: `Enum` `Rol` en `domain/rol.py` con los 6 roles del PG09 §1.1:
`DETECTOR`, `JEFE_CLD`, `TECNICO_CLD`, `RESPONSABLE_RESOLUCION`, `EJECUTOR`,
`RSGI`.

**Rationale**: PG09 fija estos roles como catálogo cerrado del procedimiento;
AGENTS.md exige modelar roles como `Enum`, nunca `str` suelto. "Detector" es
en la práctica "cualquier persona", pero como rol asignable a un `Usuario` se
mantiene en el catálogo porque el PG09 lo nombra como rol del flujo.

**Alternatives considered**: tabla de roles en BD (rechazada: el catálogo es
fijo por procedimiento certificado, no varía en runtime — cambiarlo ya
requeriría aprobación como cambio de procedimiento, igual que un `Enum`
nuevo).

## 3. Departamento

**Decision**: Value object `Departamento` (dataclass `frozen=True`)
envolviendo un `str` no vacío (trim + longitud mínima 1), sin catálogo
cerrado.

**Rationale**: El PG09 no define una lista fija de departamentos de la
organización (asunción ya recogida en spec.md). Aun así se modela como value
object, no `str` suelto, para cumplir Principio II y centralizar la única
validación (no vacío).

**Alternatives considered**: `Enum` de departamentos (rechazada: no hay lista
cerrada documentada; forzarla sería inventar alcance no pedido).

## 4. Infraestructura compartida (`shared/database.py`, `shared/uow.py`)

**Decision**: Implementar la versión mínima que `archivos` ya asume por sus
imports: `Base` (declarative base de SQLAlchemy 2.0), `engine`/
`async_sessionmaker` construidos desde `pydantic-settings`, y una clase
`UnitOfWork` con `__aenter__`/`__aexit__`, `session`, `commit()`, `rollback()`.

**Rationale**: Sin esto, `usuarios` (y `archivos`) no pueden persistir nada
real; sería solo domain+application con dobles. Se construye la versión
mínima —sin pools de conexión avanzados, sin retry, sin nada que la tarea no
pida— siguiendo el mismo contrato que ya invoca
`DocumentoRepositorySqlAlchemy`.

**Alternatives considered**: dejar `usuarios` solo con repositorio en memoria
para esta iteración (rechazada por defecto, pero señalada al usuario en
Complexity Tracking por si prefiere acotar el alcance así).

## 5. Testing async sin nuevas dependencias

**Decision**: Los tests de casos de uso (que llaman a `async def`) usan
`asyncio.run(...)` dentro de funciones de test síncronas estándar de
`pytest`; los dobles de `UsuarioRepository` son clases Python simples con
métodos `async def` que devuelven valores en memoria (mismo patrón que
`archivos` ya usa con `Protocol`).

**Rationale**: Evita añadir `pytest-asyncio`/`anyio` (TODO abierto en
AGENTS.md §6, requiere decisión/aprobación). `asyncio.run` es stdlib y basta
para tests unitarios que no necesitan fixtures async compartidas.

**Alternatives considered**: `pytest-asyncio` (rechazada por ahora: nueva
dependencia, fuera del alcance de esta feature; se deja como TODO ya
documentado en AGENTS.md).

## 6. Migraciones (Alembic)

**Decision**: Bootstrap mínimo de Alembic en la raíz del repo (`alembic.ini`,
`alembic/env.py` async, `alembic/versions/`) apuntando al `Base.metadata` de
`shared/database.py`, con la primera revisión creando la tabla `usuarios`.

**Rationale**: CLAUDE.md exige Alembic para migraciones; hoy no existe
ninguna configuración. Es infraestructura compartida, se hace una vez y sirve
para todos los módulos futuros.

**Alternatives considered**: crear la tabla a mano / `create_all()` en
arranque (rechazada: CLAUDE.md fija Alembic explícitamente como herramienta
de migraciones, no hay margen de elección aquí).
