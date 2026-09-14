from modules.usuarios.domain.Entities.usuario import Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import (
    RolInvalidoError,
    UsuarioNoEncontradoError,
)
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository


async def actualizar_usuario(
    repo: UsuarioRepository,
    correo: str,
    rol: str | None = None,
    departamento: str | None = None,
) -> Usuario:
    usuario = await repo.obtener_por_correo(correo)
    if usuario is None:
        raise UsuarioNoEncontradoError(correo)

    rol_valido: Rol | None = None
    if rol is not None:
        try:
            rol_valido = Rol(rol)
        except ValueError as error:
            raise RolInvalidoError(rol) from error

    departamento_valido = (
        Departamento(departamento) if departamento is not None else None
    )

    usuario.actualizar(rol=rol_valido, departamento=departamento_valido)
    await repo.actualizar(usuario)
    return usuario
