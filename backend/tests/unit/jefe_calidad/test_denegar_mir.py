"""Solo el jefe de CLD deniega una MIR en revision."""

import asyncio
from uuid import UUID, uuid4

import pytest

from modules.jefe_calidad.application.denegar_mir import denegar_mir
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    ActorNoAutorizadoError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.usuarios.domain.Enum.rol import Rol
from tests.unit.jefe_calidad.test_asignar_responsable import usuario_ficticio
from tests.unit.mir.test_actualizar_mir import MirRepositorioEnMemoria
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria

TECNICO = uuid4()


def mir_ficticia(
    estado: Estado = Estado.EN_REVISION, tecnico_cld_id: UUID | None = TECNICO
) -> MIR:
    return MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Se detecto una desviacion en el proceso.",
        tipo=TipoMir.INCIDENCIA,
        estado=estado,
        detectada_por_id=uuid4(),
        solucionado=False,
        tecnico_cld_id=tecnico_cld_id,
    )


def test_el_jefe_deniega_sin_tecnico_asignado_y_queda_rechazada():
    async def caso() -> None:
        mir = mir_ficticia(tecnico_cld_id=None)
        repo = MirRepositorioEnMemoria(mir)
        usuarios = UsuarioRepositoryEnMemoria()
        jefe = usuario_ficticio(Rol.JEFE_CLD)
        await usuarios.guardar(jefe)

        denegada = await denegar_mir(repo, usuarios, mir.id, jefe.id)

        assert denegada.estado == Estado.RECHAZADA
        assert repo.actualizadas == [denegada]

    asyncio.run(caso())


def test_un_tecnico_no_puede_denegar_aunque_este_asignado():
    async def caso() -> None:
        mir = mir_ficticia()
        repo = MirRepositorioEnMemoria(mir)
        usuarios = UsuarioRepositoryEnMemoria()
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        mir.tecnico_cld_id = tecnico.id
        await usuarios.guardar(tecnico)

        with pytest.raises(ActorNoAutorizadoError):
            _ = await denegar_mir(repo, usuarios, mir.id, tecnico.id)

        assert mir.estado == Estado.EN_REVISION
        assert repo.actualizadas == []

    asyncio.run(caso())


def test_un_actor_inexistente_no_puede_denegar():
    async def caso() -> None:
        mir = mir_ficticia()

        with pytest.raises(ActorNoAutorizadoError):
            _ = await denegar_mir(
                MirRepositorioEnMemoria(mir), UsuarioRepositoryEnMemoria(), mir.id, uuid4()
            )

        assert mir.estado == Estado.EN_REVISION

    asyncio.run(caso())


def test_un_jefe_inactivo_no_puede_denegar():
    async def caso() -> None:
        mir = mir_ficticia()
        usuarios = UsuarioRepositoryEnMemoria()
        jefe = usuario_ficticio(Rol.JEFE_CLD)
        jefe.dar_de_baja()
        await usuarios.guardar(jefe)

        with pytest.raises(ActorNoAutorizadoError):
            _ = await denegar_mir(MirRepositorioEnMemoria(mir), usuarios, mir.id, jefe.id)

        assert mir.estado == Estado.EN_REVISION

    asyncio.run(caso())


def test_solo_se_deniega_una_mir_en_revision():
    async def caso() -> None:
        mir = mir_ficticia(estado=Estado.EN_PROGRESO)
        usuarios = UsuarioRepositoryEnMemoria()
        jefe = usuario_ficticio(Rol.JEFE_CLD)
        await usuarios.guardar(jefe)

        with pytest.raises(EstadoInvalidoError):
            _ = await denegar_mir(MirRepositorioEnMemoria(mir), usuarios, mir.id, jefe.id)

        assert mir.estado == Estado.EN_PROGRESO

    asyncio.run(caso())


def test_no_se_deniega_una_mir_dada_de_baja():
    async def caso() -> None:
        mir = mir_ficticia()
        mir.dar_de_baja(uuid4())
        usuarios = UsuarioRepositoryEnMemoria()
        jefe = usuario_ficticio(Rol.JEFE_CLD)
        await usuarios.guardar(jefe)

        with pytest.raises(EstadoInvalidoError):
            _ = await denegar_mir(
                MirRepositorioEnMemoria(mir), usuarios, mir.id, jefe.id
            )

    asyncio.run(caso())


def test_no_se_deniega_una_mir_inexistente():
    async def caso() -> None:
        with pytest.raises(MirNoEncontradaError):
            _ = await denegar_mir(
                MirRepositorioEnMemoria(), UsuarioRepositoryEnMemoria(), uuid4(), TECNICO
            )

    asyncio.run(caso())
