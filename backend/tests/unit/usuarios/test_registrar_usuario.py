import asyncio

import pytest

from modules.usuarios.application.uses_cases.registrar_usuario import (
    registrar_usuario,
)
from modules.usuarios.domain.Exceptions.excepciones import (
    CorreoYaRegistradoError,
    DatoObligatorioFaltanteError,
    FormatoCorreoInvalidoError,
    RolInvalidoError,
)
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def test_alta_con_datos_validos_deja_el_usuario_obtenible():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        await registrar_usuario(
            repo, correo="tecnico@ainia.test", rol="TECNICO_CLD", departamento="Calidad"
        )

        usuario = await repo.obtener_por_correo("tecnico@ainia.test")
        assert usuario is not None
        assert usuario.departamento.valor == "Calidad"

    asyncio.run(caso())


def test_alta_con_correo_duplicado_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        await registrar_usuario(
            repo, correo="tecnico@ainia.test", rol="TECNICO_CLD", departamento="Calidad"
        )

        with pytest.raises(CorreoYaRegistradoError):
            await registrar_usuario(
                repo,
                correo="tecnico@ainia.test",
                rol="EJECUTOR",
                departamento="Producción",
            )

    asyncio.run(caso())


def test_alta_con_departamento_ausente_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(DatoObligatorioFaltanteError):
            await registrar_usuario(
                repo, correo="tecnico@ainia.test", rol="TECNICO_CLD", departamento=""
            )

    asyncio.run(caso())


def test_alta_con_correo_formato_invalido_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(FormatoCorreoInvalidoError):
            await registrar_usuario(
                repo,
                correo="correo-invalido",
                rol="TECNICO_CLD",
                departamento="Calidad",
            )

    asyncio.run(caso())


def test_alta_con_rol_fuera_de_catalogo_lanza_error():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()

        with pytest.raises(RolInvalidoError):
            await registrar_usuario(
                repo,
                correo="tecnico@ainia.test",
                rol="ROL_INVENTADO",
                departamento="Calidad",
            )

    asyncio.run(caso())
