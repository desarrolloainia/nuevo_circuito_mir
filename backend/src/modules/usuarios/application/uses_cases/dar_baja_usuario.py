from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository


async def dar_baja_usuario(repo: UsuarioRepository, correo: str) -> None:
    usuario = await repo.obtener_por_correo(correo)
    if usuario is None:
        raise UsuarioNoEncontradoError(correo)

    usuario.dar_de_baja()
    await repo.actualizar(usuario)
