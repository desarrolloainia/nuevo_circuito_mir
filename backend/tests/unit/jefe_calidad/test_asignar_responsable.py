"""El jefe de CLD designa al tecnico de CLD que gestiona la MIR."""

import asyncio
from uuid import uuid4

import pytest

from modules.jefe_calidad.application.asignar_responsable import (
    UsuarioNoEsTecnicoCldError,
    asignar_responsable,
)
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from tests.unit.mir.test_actualizar_mir import MirRepositorioEnMemoria
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def mir_ficticia() -> MIR:
    return MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Se detecto una desviacion en el proceso.",
        tipo=TipoMir.INCIDENCIA,
        estado=Estado.EN_REVISION,
        detectada_por_id=uuid4(),
        solucionado=False,
    )


def usuario_ficticio(rol: Rol) -> Usuario:
    return Usuario(
        correo=Correo(f"{uuid4().hex}@ejemplo.test"),
        nombre="Usuario Ficticio",
        rol=rol,
        departamento=Departamento("CLD"),
    )


async def repos(
    mir: MIR, *usuarios: Usuario
) -> tuple[MirRepositorioEnMemoria, UsuarioRepositoryEnMemoria]:
    usuario_repo = UsuarioRepositoryEnMemoria()
    for usuario in usuarios:
        await usuario_repo.guardar(usuario)
    return MirRepositorioEnMemoria(mir), usuario_repo


def test_un_tecnico_de_cld_queda_asignado_a_la_mir_y_se_persiste():
    async def caso() -> None:
        mir = mir_ficticia()
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        mir_repo, usuario_repo = await repos(mir, tecnico)

        asignada = await asignar_responsable(mir_repo, usuario_repo, mir.id, tecnico.id)

        assert asignada.tecnico_cld_id == tecnico.id
        assert asignada.estado == Estado.EN_PROGRESO
        assert mir_repo.actualizadas == [asignada]

    asyncio.run(caso())


def test_un_usuario_sin_rol_de_tecnico_de_cld_no_se_puede_asignar():
    async def caso() -> None:
        mir = mir_ficticia()
        ejecutor = usuario_ficticio(Rol.EJECUTOR)
        mir_repo, usuario_repo = await repos(mir, ejecutor)

        with pytest.raises(UsuarioNoEsTecnicoCldError):
            _ = await asignar_responsable(mir_repo, usuario_repo, mir.id, ejecutor.id)

        assert mir.tecnico_cld_id is None
        assert mir_repo.actualizadas == []

    asyncio.run(caso())


def test_un_tecnico_dado_de_baja_no_se_puede_asignar():
    async def caso() -> None:
        mir = mir_ficticia()
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        tecnico.dar_de_baja()
        mir_repo, usuario_repo = await repos(mir, tecnico)

        with pytest.raises(UsuarioNoEncontradoError):
            _ = await asignar_responsable(mir_repo, usuario_repo, mir.id, tecnico.id)

    asyncio.run(caso())


def test_no_se_asigna_tecnico_a_una_mir_inexistente():
    async def caso() -> None:
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        _, usuario_repo = await repos(mir_ficticia(), tecnico)

        with pytest.raises(MirNoEncontradaError):
            _ = await asignar_responsable(
                MirRepositorioEnMemoria(), usuario_repo, uuid4(), tecnico.id
            )

    asyncio.run(caso())


def test_no_se_asigna_tecnico_a_una_mir_dada_de_baja():
    async def caso() -> None:
        mir = mir_ficticia()
        mir.dar_de_baja(uuid4())
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        mir_repo, usuario_repo = await repos(mir, tecnico)

        with pytest.raises(EstadoInvalidoError):
            _ = await asignar_responsable(mir_repo, usuario_repo, mir.id, tecnico.id)

        assert mir.tecnico_cld_id is None

    asyncio.run(caso())


def test_no_se_asigna_tecnico_a_una_mir_fuera_de_revision():
    async def caso() -> None:
        mir = mir_ficticia()
        mir.estado = Estado.RECHAZADA
        tecnico = usuario_ficticio(Rol.TECNICO_CLD)
        mir_repo, usuario_repo = await repos(mir, tecnico)

        with pytest.raises(EstadoInvalidoError):
            _ = await asignar_responsable(mir_repo, usuario_repo, mir.id, tecnico.id)

        assert mir.estado == Estado.RECHAZADA
        assert mir.tecnico_cld_id is None
        assert mir_repo.actualizadas == []

    asyncio.run(caso())
