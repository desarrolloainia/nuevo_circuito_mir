from modules.usuarios.domain.Entities.usuario import Usuario
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository


async def listar_usuarios(repo: UsuarioRepository) -> list[Usuario]:
    return await repo.listar_activos()
