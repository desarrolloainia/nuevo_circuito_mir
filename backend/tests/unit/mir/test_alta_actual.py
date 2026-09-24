"""Contrato del alta y comportamiento observable sin base de datos."""

import asyncio
from datetime import date, datetime
from typing import Self, cast
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from modules.mir.api.dto import CrearMirDTO
from modules.mir.application.uses_cases.crear_mir import crear_mir
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.repository.mir_repository import MirRepository
from modules.mir.infrastructure.db.persistance.mir_repository import to_domain, to_orm
from shared.uow import UnitOfWork


def datos_validos() -> dict[str, object]:
    return {
        "tipo": "Incidencia",
        "descripcion": "Desviacion de prueba.",
        "fecha_deteccion": "2026-09-20",
        "detectada_por_id": str(uuid4()),
        "solucionado": False,
        "empresa_nombre": "Empresa Ficticia",
        "persona_contacto": "Persona Ficticia",
        "telefono": "+34 0600123456",
        "correo_electronico": "contacto@ejemplo.test",
    }


def test_alta_no_exige_codigo_ni_estado_y_acepta_telefono_como_texto() -> None:
    datos = CrearMirDTO.model_validate(datos_validos())

    assert datos.fecha_deteccion == date(2026, 9, 20)
    assert datos.telefono == "+34 0600123456"
    assert "codigo_mir" not in datos.model_dump()
    assert "estado" not in datos.model_dump()


def test_no_admite_una_fecha_futura_ni_un_contacto_vacio() -> None:
    datos = datos_validos()
    datos.update(fecha_deteccion="2999-01-01", empresa_nombre="")

    with pytest.raises(ValidationError):
        _ = CrearMirDTO.model_validate(datos)


def test_un_alta_sin_adjuntos_reserva_codigo_y_persiste_datos() -> None:
    class Repositorio:
        def __init__(self) -> None:
            self.mir: MIR | None = None

        async def reservar_numero(self, anio: int) -> int:
            assert anio == datetime.now(ZoneInfo("Europe/Madrid")).year
            return 1

        async def create_mir(self, mir: MIR) -> MIR:
            self.mir = mir
            return mir

    class Uow:
        def __init__(self) -> None:
            self.commits = 0

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def commit(self) -> None:
            self.commits += 1

    async def caso() -> None:
        repo = Repositorio()
        uow = Uow()
        datos = CrearMirDTO.model_validate(datos_validos())
        mir = await crear_mir(
            descripcion=datos.descripcion,
            tipo=datos.tipo,
            fecha_deteccion=datos.fecha_deteccion,
            detectada_por_id=datos.detectada_por_id,
            solucionado=datos.solucionado,
            empresa_nombre=datos.empresa_nombre,
            persona_contacto=datos.persona_contacto,
            telefono=datos.telefono,
            correo_electronico=datos.correo_electronico,
            adjuntos=[],
            storage=None,
            documento_repositorio=cast(DocumentoRepository, None),
            mir_repositorio=cast(MirRepository, repo),
            uow=cast(UnitOfWork, uow),
        )

        assert repo.mir is mir
        assert (
            mir.codigo_mir
            == f"{datetime.now(ZoneInfo('Europe/Madrid')).year % 100:02d}001"
        )
        assert mir.fecha_deteccion == date(2026, 9, 20)
        assert mir.empresa_nombre == "Empresa Ficticia"
        assert uow.commits == 1

    asyncio.run(caso())


def test_los_datos_del_formulario_se_mapean_a_la_base_y_de_vuelta() -> None:
    mir = MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Incidencia ficticia",
        tipo=TipoMir.INCIDENCIA,
        estado=Estado.EN_REVISION,
        detectada_por_id=uuid4(),
        solucionado=False,
        fecha_deteccion=date(2026, 9, 20),
        empresa_nombre="Empresa Ficticia",
        persona_contacto="Persona Ficticia",
        telefono="0600123456",
        correo_electronico="contacto@ejemplo.test",
        nombre_comercial="Comercial Ficticio",
        codigo_cliente="CLIENTE-1",
    )

    recuperada = to_domain(to_orm(mir))

    assert recuperada.fecha_deteccion == mir.fecha_deteccion
    assert recuperada.empresa_nombre == mir.empresa_nombre
    assert recuperada.persona_contacto == mir.persona_contacto
    assert recuperada.telefono == mir.telefono
    assert recuperada.correo_electronico == mir.correo_electronico
    assert recuperada.nombre_comercial == mir.nombre_comercial
    assert recuperada.codigo_cliente == mir.codigo_cliente
