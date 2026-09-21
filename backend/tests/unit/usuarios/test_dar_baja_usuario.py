import asyncio

import pytest

from modules.usuarios.application.uses_cases.dar_baja_usuario import (
    dar_baja_usuario,
)
from modules.usuarios.application.uses_cases.listar_usuarios import listar_usuarios
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def test_dar_baja_desaparece_del_listado_pero_sigue_consultable():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        await repo.guardar(
            Usuario(
                correo=Correo("tecnico@ainia.test"),
                nombre="Ana Técnico",
                rol=Rol.TECNICO_CLD,
                departamento=Departamento("Calidad"),
            )
        )

        await dar_baja_usuario(repo, "tecnico@ainia.test")

        assert await listar_usuarios(repo) == []
        usuario = await repo.obtener_por_correo("tecnico@ainia.test")
        assert usuario is not None
        assert usuario.activo is False

    asyncio.run(caso())


def test_dar_baja_con_correo_inexistente_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(UsuarioNoEncontradoError):
            await dar_baja_usuario(repo, "no-existe@ainia.test")

    asyncio.run(caso())


def test_dar_baja_es_idempotente():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        await repo.guardar(
            Usuario(
                correo=Correo("tecnico@ainia.test"),
                nombre="Ana Técnico",
                rol=Rol.TECNICO_CLD,
                departamento=Departamento("Calidad"),
            )
        )

        await dar_baja_usuario(repo, "tecnico@ainia.test")
        await dar_baja_usuario(repo, "tecnico@ainia.test")

        usuario = await repo.obtener_por_correo("tecnico@ainia.test")
        assert usuario is not None
        assert usuario.activo is False

    asyncio.run(caso())
