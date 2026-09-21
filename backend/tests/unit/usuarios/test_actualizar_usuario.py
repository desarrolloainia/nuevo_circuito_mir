import asyncio

import pytest

from modules.usuarios.application.uses_cases.actualizar_usuario import (
    actualizar_usuario,
)
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import (
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def test_actualizar_usuario_activo_cambia_rol_y_departamento():
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

        usuario = await actualizar_usuario(
            repo, "tecnico@ainia.test", rol="EJECUTOR", departamento="Producción"
        )

        assert usuario.rol == Rol.EJECUTOR
        assert usuario.departamento.valor == "Producción"

    asyncio.run(caso())


def test_actualizar_usuario_activo_cambia_nombre():
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

        usuario = await actualizar_usuario(
            repo, "tecnico@ainia.test", nombre="Ana Gómez"
        )

        assert usuario.nombre == "Ana Gómez"

    asyncio.run(caso())


def test_actualizar_usuario_con_correo_inexistente_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(UsuarioNoEncontradoError):
            await actualizar_usuario(
                repo, "no-existe@ainia.test", departamento="Calidad"
            )

    asyncio.run(caso())


def test_actualizar_usuario_inactivo_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        usuario = Usuario(
            correo=Correo("tecnico@ainia.test"),
            nombre="Ana Técnico",
            rol=Rol.TECNICO_CLD,
            departamento=Departamento("Calidad"),
        )
        usuario.dar_de_baja()
        await repo.guardar(usuario)

        with pytest.raises(UsuarioInactivoError):
            await actualizar_usuario(
                repo, "tecnico@ainia.test", departamento="Producción"
            )

    asyncio.run(caso())
