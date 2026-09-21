# API Contract: `/usuarios`

Router: `APIRouter(prefix="/usuarios", tags=["Usuarios"])`, mismo estilo que
`archivos/api/router.py`.

## POST /usuarios

Crea un usuario (US1).

**Request body**:
```json
{
  "nombre": "Ana Gómez",
  "correo": "persona@ainia.es",
  "rol": "TECNICO_CLD",
  "departamento": "Calidad"
}
```

**Responses**:
- `201 Created` — devuelve el usuario creado (ver `UsuarioRead` abajo).
- `409 Conflict` — correo ya registrado (`CorreoYaRegistradoError`).
- `422 Unprocessable Entity` — correo con formato inválido, rol fuera del
  catálogo, o falta algún campo obligatorio.

## GET /usuarios

Lista usuarios activos (US2).

**Query params**: ninguno en esta fase (sin paginación/filtros — YAGNI hasta
que haga falta).

**Response**: `200 OK` con `list[UsuarioRead]`.

## GET /usuarios/{correo}

Consulta un usuario por correo (US2).

**Responses**:
- `200 OK` con `UsuarioRead` (incluye usuarios inactivos también, para poder
  consultar el histórico).
- `404 Not Found` — no existe usuario con ese correo.

## PATCH /usuarios/{correo}

Actualiza nombre, rol y/o departamento de un usuario activo (US3).

**Request body** (los tres opcionales, al menos uno presente):
```json
{
  "nombre": "Ana Gómez",
  "rol": "EJECUTOR",
  "departamento": "Producción"
}
```

**Responses**:
- `200 OK` con `UsuarioRead` actualizado.
- `404 Not Found` — no existe usuario con ese correo.
- `409 Conflict` — el usuario está inactivo (no se puede actualizar).
- `422 Unprocessable Entity` — rol fuera de catálogo o departamento vacío.

## DELETE /usuarios/{correo}

Da de baja lógicamente al usuario (US3, FR-009). Semánticamente es un
`DELETE` para el cliente HTTP, pero internamente solo cambia
`activo=False` y fija `dado_de_baja_en` — nunca borra la fila (Principio V).

**Responses**:
- `204 No Content` — baja realizada (idempotente: si ya estaba inactivo,
  también `204`).
- `404 Not Found` — no existe usuario con ese correo.

## Esquema `UsuarioRead` (respuesta común)

```json
{
  "id": "uuid",
  "correo": "persona@ainia.es",
  "nombre": "Ana Gómez",
  "rol": "TECNICO_CLD",
  "departamento": "Calidad",
  "activo": true,
  "creado_en": "2026-09-11T10:00:00Z",
  "dado_de_baja_en": null
}
```

Fuera de alcance en esta fase (según spec.md, Assumptions): cualquier
endpoint de login/autenticación, cambio de contraseña, o gestión de sesión.
