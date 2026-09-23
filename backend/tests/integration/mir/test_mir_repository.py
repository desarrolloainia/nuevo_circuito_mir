"""Contador anual y vinculacion documental contra PostgreSQL."""

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.mir.infrastructure.db.persistence.mir_repository import (
    MirRepositorySqlAlchemy,
)
from sqlalchemy import text

from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from modules.archivos.infrastructure.db.entities.documento import DocumentoORM
from modules.archivos.infrastructure.db.persistence.documento_repository import (
    DocumentoRepositorySqlAlchemy,
)
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.tipo import TipoMir
from shared.uow import UnitOfWork

AHORA = datetime.now(UTC)


def mir_de_prueba(detector_id: UUID, codigo: str) -> MIR:
    return MIR(
        codigo_mir=codigo,
        descripcion="Desviacion ficticia detectada en una prueba.",
        tipo=TipoMir.INCIDENCIA,
        fecha_deteccion=AHORA.date(),
        detectada_por_id=detector_id,
        solucionado=False,
        creado_en=AHORA,
    )


async def reservar(
    crear_uow: Callable[[], UnitOfWork], anio: int, confirmar: bool = True
) -> int:
    uow = crear_uow()
    async with uow:
        numero = await MirRepositorySqlAlchemy(uow).reservar_numero(anio)
        if confirmar:
            await uow.commit()
        return numero


def test_las_reservas_del_mismo_anio_son_consecutivas(
    crear_uow: Callable[[], UnitOfWork],
):
    async def caso() -> None:
        assert [await reservar(crear_uow, 2026) for _ in range(3)] == [1, 2, 3]

    asyncio.run(caso())


def test_cada_anio_reinicia_su_secuencia(crear_uow: Callable[[], UnitOfWork]):
    async def caso() -> None:
        assert await reservar(crear_uow, 2026) == 1
        assert await reservar(crear_uow, 2027) == 1
        assert await reservar(crear_uow, 2026) == 2

    asyncio.run(caso())


def test_la_secuencia_puede_superar_el_millar(crear_uow: Callable[[], UnitOfWork]):
    async def caso() -> None:
        uow = crear_uow()
        async with uow:
            _ = await uow.session.execute(
                text(
                    "insert into contadores_codigo_mir (anio, ultimo_numero) values (2026, 999)"
                )
            )
            await uow.commit()

        assert await reservar(crear_uow, 2026) == 1000

    asyncio.run(caso())


def test_un_rollback_posterior_a_la_reserva_no_consume_codigo(
    crear_uow: Callable[[], UnitOfWork],
):
    async def caso() -> None:
        assert await reservar(crear_uow, 2026, confirmar=False) == 1
        assert await reservar(crear_uow, 2026) == 1

    asyncio.run(caso())


def test_cincuenta_altas_simultaneas_obtienen_codigos_distintos(
    crear_uow: Callable[[], UnitOfWork],
):
    async def caso() -> None:
        numeros = await asyncio.gather(*(reservar(crear_uow, 2026) for _ in range(50)))
        assert sorted(numeros) == list(range(1, 51))

    asyncio.run(caso())


def test_la_mir_guardada_se_recupera_con_su_codigo(
    crear_uow: Callable[[], UnitOfWork], usuario_ficticio: UUID
):
    async def caso() -> None:
        uow = crear_uow()
        async with uow:
            mir = await MirRepositorySqlAlchemy(uow).guardar(
                mir_de_prueba(usuario_ficticio, "26001")
            )
            await uow.commit()

        uow = crear_uow()
        async with uow:
            fila = await uow.session.execute(
                text("select codigo_mir, estado from mirs where id = :id"),
                {"id": mir.id},
            )
            assert fila.one() == ("26001", "EN_REVISION")

    asyncio.run(caso())


async def crear_documento(crear_uow: Callable[[], UnitOfWork], creador: UUID) -> UUID:
    documento_id = uuid4()
    uow = crear_uow()
    async with uow:
        uow.session.add(
            DocumentoORM(
                id=documento_id,
                nombre="evidencia-ficticia.pdf",
                tipo=TipoDocumento.PDF,
                storage_id=f"remoto-{documento_id.hex}",
                tamano_bytes=1024,
                creado_por=creador,
                mir_id=None,
                creado_en=AHORA,
            )
        )
        await uow.commit()
    return documento_id


def test_el_bloqueo_devuelve_la_mir_actual_de_cada_documento_existente(
    crear_uow: Callable[[], UnitOfWork], usuario_ficticio: UUID
):
    async def caso() -> None:
        documento_id = await crear_documento(crear_uow, usuario_ficticio)
        inexistente = uuid4()

        uow = crear_uow()
        async with uow:
            estado = await DocumentoRepositorySqlAlchemy(uow).bloquear(
                [inexistente, documento_id]
            )

        assert estado == {documento_id: None}

    asyncio.run(caso())


def test_los_documentos_se_vinculan_todos_o_ninguno(
    crear_uow: Callable[[], UnitOfWork], usuario_ficticio: UUID
):
    async def caso() -> None:
        documentos = [
            await crear_documento(crear_uow, usuario_ficticio) for _ in range(2)
        ]

        uow = crear_uow()
        async with uow:
            repositorio = MirRepositorySqlAlchemy(uow)
            mir = await repositorio.guardar(mir_de_prueba(usuario_ficticio, "26002"))
            await DocumentoRepositorySqlAlchemy(uow).vincular(documentos, mir.id)
            # Sin commit: la salida del contexto revierte MIR y vinculos.

        uow = crear_uow()
        async with uow:
            estado = await DocumentoRepositorySqlAlchemy(uow).bloquear(documentos)
        assert set(estado.values()) == {None}

    asyncio.run(caso())


def test_dos_altas_no_pueden_vincular_el_mismo_documento(
    crear_uow: Callable[[], UnitOfWork], usuario_ficticio: UUID
):
    async def caso() -> None:
        documento_id = await crear_documento(crear_uow, usuario_ficticio)

        async def vincular(codigo: str, retardo: float) -> UUID | None:
            uow = crear_uow()
            async with uow:
                estado = await DocumentoRepositorySqlAlchemy(uow).bloquear(
                    [documento_id]
                )
                if estado.get(documento_id) is not None:
                    return None
                await asyncio.sleep(retardo)
                mir = await MirRepositorySqlAlchemy(uow).guardar(
                    mir_de_prueba(usuario_ficticio, codigo)
                )
                await DocumentoRepositorySqlAlchemy(uow).vincular(
                    [documento_id], mir.id
                )
                await uow.commit()
                return mir.id

        primera, segunda = await asyncio.gather(
            vincular("26003", 0.2), vincular("26004", 0.0)
        )

        uow = crear_uow()
        async with uow:
            estado = await DocumentoRepositorySqlAlchemy(uow).bloquear([documento_id])
        assert estado[documento_id] in {primera, segunda}
        assert None in (primera, segunda) or primera != segunda

    asyncio.run(caso())
