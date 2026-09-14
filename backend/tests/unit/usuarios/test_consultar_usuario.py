import asyncio

import pytest

from modules.usuarios.application.uses_cases.consultar_usuario import (
    consultar_usuario,
)
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def test_consultar_usuario_por_correo_devuelve_sus_datos():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        await repo.guardar(
            Usuario(
                correo=Correo("tecnico@ainia.test"),
                rol=Rol.TECNICO_CLD,
                departamento=Departamento("Calidad"),
            )
        )

        usuario = await consultar_usuario(repo, "tecnico@ainia.test")

        assert usuario.correo.valor == "tecnico@ainia.test"
        assert usuario.rol == Rol.TECNICO_CLD
        assert usuario.departamento.valor == "Calidad"

    asyncio.run(caso())


def test_consultar_usuario_con_correo_inexistente_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(UsuarioNoEncontradoError):
            await consultar_usuario(repo, "no-existe@ainia.test")

    asyncio.run(caso())
