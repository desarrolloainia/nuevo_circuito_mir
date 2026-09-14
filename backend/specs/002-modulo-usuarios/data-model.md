# Data Model: Módulo Usuarios

## Value Objects

### `Correo`
- Envuelve un `str`.
- Validación: coincide con `^[^@\s]+@[^@\s]+\.[^@\s]+$`; si no, lanza
  `FormatoCorreoInvalidoError`.
- Es el identificador único del `Usuario` (no hay `id` de negocio separado
  del correo a efectos de búsqueda, aunque la entidad tenga un `UUID` técnico
  como clave primaria de persistencia).

### `Departamento`
- Envuelve un `str` no vacío (tras `strip()`).
- Validación: si queda vacío, lanza `DatoObligatorioFaltanteError("departamento")`.

### `Rol` (Enum)
Catálogo cerrado, PG09 §1.1:
- `DETECTOR`
- `JEFE_CLD`
- `TECNICO_CLD`
- `RESPONSABLE_RESOLUCION`
- `EJECUTOR`
- `RSGI`

## Entidad: `Usuario`

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | `UUID` | Generado al crear (`default_factory=uuid4`); clave técnica de persistencia. |
| `correo` | `Correo` | Único en el sistema (FR-003); inmutable tras el alta (no hay FR que permita cambiar el correo). |
| `rol` | `Rol` | Obligatorio; debe pertenecer al catálogo cerrado (FR-004). |
| `departamento` | `Departamento` | Obligatorio (FR-005). |
| `activo` | `bool` | `True` al crear; pasa a `False` con la baja lógica (FR-009). Nunca se elimina el registro. |
| `creado_en` | `datetime` (UTC) | `default_factory=lambda: datetime.now(UTC)`. |
| `dado_de_baja_en` | `datetime \| None` | `None` mientras `activo=True`; se fija al dar de baja (trazabilidad, Principio V). |

**Invariantes de la entidad**:
- No puede construirse sin `correo`, `rol` y `departamento` válidos (FR-001,
  FR-005) — la validación ocurre en el `__init__`/value objects, no en el
  router.
- `dar_de_baja()`: si ya está inactivo, no hace nada idempotente (no lanza
  error) — dar de baja dos veces no es un caso de error de negocio.
- `actualizar(rol=None, departamento=None)`: solo puede aplicarse sobre un
  usuario activo; si el usuario está inactivo, no se expone actualización vía
  caso de uso (se da de alta uno nuevo o se reactiva en una iteración futura,
  fuera de alcance de esta spec).

## Relaciones con otros módulos

- `mir` referenciará en el futuro a `Usuario` (por `correo` o `id`) como
  detector/responsable/ejecutor, a través de un puerto que `mir/domain`
  declare — **no** implementado en esta feature (fuera de alcance de
  spec.md, que es solo el módulo `usuarios` en sí mismo).

## Errores de dominio (`domain/excepciones.py`)

- `CorreoYaRegistradoError` — alta con correo duplicado (FR-003, Edge Case).
- `RolInvalidoError` — valor de rol fuera del catálogo (FR-004, Edge Case).
- `FormatoCorreoInvalidoError` — correo con formato inválido (FR-002, Edge Case).
- `DatoObligatorioFaltanteError` — falta correo, rol o departamento (FR-005).
- `UsuarioNoEncontradoError` — consulta/actualización sobre un correo
  inexistente (Acceptance Scenario US2-3).

## Persistencia (SQLAlchemy, tabla `usuarios`)

| Columna | Tipo SQLAlchemy | Notas |
|---|---|---|
| `id` | `UUID(as_uuid=True)`, PK | igual convención que `documentos.id` en `archivos` |
| `correo` | `String`, `unique=True`, `index=True` | constraint de unicidad a nivel de BD, no solo de dominio |
| `rol` | `SqlEnum(Rol)` | mismo patrón que `TipoDocumento` en `archivos` |
| `departamento` | `String` | |
| `activo` | `Boolean`, `default=True` | |
| `creado_en` | `DateTime(timezone=True)` | |
| `dado_de_baja_en` | `DateTime(timezone=True)`, nullable | |
