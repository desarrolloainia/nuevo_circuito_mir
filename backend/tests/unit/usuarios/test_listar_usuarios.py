import asyncio

from modules.usuarios.application.uses_cases.listar_usuarios import listar_usuarios
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria


def test_listar_usuarios_devuelve_solo_los_activos():
    async def caso() -> None:
        repo = UsuarioRepositoryEnMemoria()
        activo = Usuario(
            correo=Correo("activo@ainia.test"),
            rol=Rol.TECNICO_CLD,
            departamento=Departamento("Calidad"),
        )
        inactivo = Usuario(
            correo=Correo("inactivo@ainia.test"),
            rol=Rol.EJECUTOR,
            departamento=Departamento("Producción"),
        )
        inactivo.dar_de_baja()
        await repo.guardar(activo)
        await repo.guardar(inactivo)

        usuarios = await listar_usuarios(repo)

        correos = {usuario.correo.valor for usuario in usuarios}
        assert correos == {"activo@ainia.test"}

    asyncio.run(caso())
