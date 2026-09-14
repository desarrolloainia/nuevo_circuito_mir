# Quickstart: Validar el módulo Usuarios

## Prerrequisitos

- `uv sync` ejecutado (entorno con FastAPI, SQLAlchemy, asyncpg, alembic).
- PostgreSQL de desarrollo/test accesible y configurado vía `pydantic-settings`
  (variables de entorno leídas por `shared/database.py`, nunca hardcodeadas).
- Migración de `usuarios` aplicada: `uv run alembic upgrade head`.

## Validación por tests (camino recomendado, sin levantar el servidor)

```bash
uv run pytest tests/unit/usuarios -v
uv run pytest tests/integration/usuarios -v
```

Cubre, como mínimo (ver spec.md Acceptance Scenarios):
- Alta con datos válidos → usuario consultable.
- Alta con correo duplicado → rechazada.
- Alta con dato obligatorio ausente → rechazada.
- Alta con correo de formato inválido → rechazada.
- Alta con rol fuera del catálogo → rechazada.
- Actualización de rol/departamento → reflejada en consulta posterior.
- Baja lógica → desaparece del listado de activos, sigue consultable por
  correo, y una actualización posterior sobre él es rechazada.

## Validación end-to-end (con el servidor levantado)

```bash
uv run fastapi dev  # o el comando de arranque que exponga la app FastAPI
```

1. Dar de alta un usuario:
   ```bash
   curl -X POST http://localhost:8000/usuarios \
     -H "Content-Type: application/json" \
     -d '{"correo":"tecnico@ainia.es","rol":"TECNICO_CLD","departamento":"Calidad"}'
   ```
   Esperado: `201` con el usuario creado (ver `contracts/usuarios-api.md`).

2. Repetir el mismo alta → esperado `409 Conflict` (correo duplicado).

3. Consultar el listado:
   ```bash
   curl http://localhost:8000/usuarios
   ```
   Esperado: incluye el usuario creado en el paso 1.

4. Actualizar su departamento:
   ```bash
   curl -X PATCH http://localhost:8000/usuarios/tecnico@ainia.es \
     -H "Content-Type: application/json" -d '{"departamento":"Producción"}'
   ```
   Esperado: `200` con `departamento` actualizado.

5. Dar de baja:
   ```bash
   curl -X DELETE http://localhost:8000/usuarios/tecnico@ainia.es
   ```
   Esperado: `204`. Repetir el listado (paso 3) → el usuario ya no aparece.
   Consultar por correo (`GET /usuarios/tecnico@ainia.es`) → sigue devolviendo
   `200` con `"activo": false`.

## Definición de terminado

`uv run pytest`, `uv run ruff check --fix .`, `uv run ruff format .` y
`uv run basedpyright` pasan en limpio (CLAUDE.md §3).
