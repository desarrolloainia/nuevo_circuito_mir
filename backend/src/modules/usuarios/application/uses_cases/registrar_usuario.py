from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import (
    CorreoYaRegistradoError,
    RolInvalidoError,
)
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository


async def registrar_usuario(
    repo: UsuarioRepository, correo: str, rol: str, departamento: str, nombre: str
) -> Usuario:
    try:
        rol_valido = Rol(rol)
    except ValueError as error:
        raise RolInvalidoError(rol) from error

    if await repo.obtener_por_correo(correo) is not None:
        raise CorreoYaRegistradoError(correo)

    usuario = Usuario(
        correo=Correo(correo),
        rol=rol_valido,
        departamento=Departamento(departamento),
        nombre=nombre,
    )
    await repo.guardar(usuario)
    return usuario
