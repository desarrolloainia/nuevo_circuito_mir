from modules.usuarios.domain.Entities.usuario import Usuario
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository


async def consultar_usuario(repo: UsuarioRepository, correo: str) -> Usuario:
    usuario = await repo.obtener_por_correo(correo)
    if usuario is None:
        raise UsuarioNoEncontradoError(correo)
    return usuario
