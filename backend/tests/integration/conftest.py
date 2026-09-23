"""Fixtures de integracion sobre una base PostgreSQL desechable.

Nunca se usa la base de desarrollo ni SharePoint real: la base se crea y se
destruye en cada sesion de pruebas y los datos son ficticios.
"""

import asyncio
import os
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from importlib import import_module
from typing import cast
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from modules.mir.infrastructure.db.entities.contador_codigo_mir import (  # noqa: F401
    ContadorCodigoMirORM,
)
from sqlalchemy import NullPool
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from modules.archivos.application.ports.file_storage import (
    ArchivoSubido,
    FileStorageError,
)
from modules.archivos.infrastructure.db.entities.documento import (
    DocumentoORM,  # noqa: F401
)
from modules.mir.infrastructure.db.entities.mir import MirORM  # noqa: F401
from modules.usuarios.Infrastructure.entities.usuario import UsuarioORM
from shared.database import Base
from shared.uow import UnitOfWork

TABLAS = ("documentos", "mirs", "contadores_codigo_mir", "usuarios")


def _url_administracion() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL no definida")
    return url


async def _ejecutar_en_autocommit(url: str, sentencias: list[str]) -> None:
    motor = create_async_engine(url, isolation_level="AUTOCOMMIT")
    try:
        async with motor.connect() as conexion:
            for sentencia in sentencias:
                _ = await conexion.exec_driver_sql(sentencia)
    finally:
        await motor.dispose()


@pytest.fixture(scope="session")
def url_base_desechable() -> Iterator[str]:
    """Crea una base vacia solo para esta sesion y la elimina al terminar."""
    url_admin = make_url(_url_administracion())
    nombre = f"circuito_mir_test_{uuid4().hex[:12]}"
    url_nueva = url_admin.set(database=nombre)
    try:
        asyncio.run(
            _ejecutar_en_autocommit(
                url_admin.render_as_string(hide_password=False),
                [f'create database "{nombre}"'],
            )
        )
    except Exception as error:  # noqa: BLE001 - sin PostgreSQL no hay integracion
        pytest.skip(f"PostgreSQL no disponible: {type(error).__name__}")

    yield url_nueva.render_as_string(hide_password=False)

    asyncio.run(
        _ejecutar_en_autocommit(
            url_admin.render_as_string(hide_password=False),
            [
                f"select pg_terminate_backend(pid) from pg_stat_activity where datname = '{nombre}'",
                f'drop database if exists "{nombre}"',
            ],
        )
    )


@pytest.fixture(scope="session")
def motor(url_base_desechable: str) -> Iterator[AsyncEngine]:
    # NullPool: cada test usa su propio bucle de eventos y una conexion
    # asyncpg no puede reutilizarse entre bucles distintos.
    motor = create_async_engine(url_base_desechable, poolclass=NullPool)

    async def crear_esquema() -> None:
        async with motor.begin() as conexion:
            _ = await conexion.run_sync(Base.metadata.create_all)

    asyncio.run(crear_esquema())
    yield motor
    asyncio.run(motor.dispose())


@pytest.fixture
def sesiones(motor: AsyncEngine) -> Iterator[async_sessionmaker[AsyncSession]]:
    """Fabrica de sesiones independientes; cada UnitOfWork abre la suya."""

    async def limpiar() -> None:
        async with motor.begin() as conexion:
            _ = await conexion.exec_driver_sql(
                f"truncate {', '.join(TABLAS)} restart identity cascade"
            )

    asyncio.run(limpiar())
    yield async_sessionmaker(bind=motor, class_=AsyncSession)
    asyncio.run(limpiar())


@pytest.fixture
def crear_uow(sesiones: async_sessionmaker[AsyncSession]) -> Callable[[], UnitOfWork]:
    return lambda: UnitOfWork(sesiones)


@pytest.fixture
def usuario_ficticio(crear_uow: Callable[[], UnitOfWork]) -> UUID:
    """Inserta un usuario de prueba con datos inventados y devuelve su id."""
    usuario_id = uuid4()

    async def insertar() -> None:
        uow = crear_uow()
        async with uow:
            uow.session.add(
                UsuarioORM(
                    id=usuario_id,
                    correo=f"ficticio-{usuario_id.hex[:8]}@ejemplo.test",
                    rol="DETECTOR",
                    nombre="Persona Ficticia",
                    departamento="Departamento Ficticio",
                    activo=True,
                    creado_en=datetime.now(UTC),
                )
            )
            await uow.commit()

    asyncio.run(insertar())
    return usuario_id


class StorageEnMemoria:
    """Doble del almacenamiento documental: ningun test llama a SharePoint."""

    def __init__(self) -> None:
        self.archivos: dict[str, bytes] = {}
        self.fallar = False

    async def subir(
        self, nombre: str, contenido: bytes, content_type: str
    ) -> ArchivoSubido:
        if self.fallar:
            raise FileStorageError("almacenamiento no disponible")
        storage_id = f"remoto-{uuid4().hex}"
        self.archivos[storage_id] = contenido
        return ArchivoSubido(
            storage_id=storage_id, nombre=nombre, tamano_bytes=len(contenido)
        )

    async def eliminar(self, storage_id: str) -> None:
        _ = self.archivos.pop(storage_id, None)

    async def descargar(self, storage_id: str) -> bytes:
        return self.archivos[storage_id]


@pytest.fixture
def storage() -> StorageEnMemoria:
    return StorageEnMemoria()


@pytest.fixture
def cliente(
    crear_uow: Callable[[], UnitOfWork], storage: StorageEnMemoria
) -> Iterator[TestClient]:
    from modules.archivos.api import router as subida_router
    from modules.mir.api import router as router_mir

    app = cast(FastAPI, import_module("main").app)
    # Se conservan las inyecciones del composition root; solo se sustituyen la
    # transaccion y el almacenamiento remoto.
    originales = dict(app.dependency_overrides)
    app.dependency_overrides[router_mir.get_uow] = crear_uow
    app.dependency_overrides[subida_router.get_uow] = crear_uow
    app.dependency_overrides[subida_router.get_storage] = lambda: storage
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
    app.dependency_overrides.update(originales)
