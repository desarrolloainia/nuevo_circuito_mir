from modules.usuarios.domain.Entities.usuario import Usuario


class UsuarioRepositoryEnMemoria:
    """Doble de test escrito a mano para UsuarioRepository (sin mocks)."""

    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}

    async def guardar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.correo.valor] = usuario

    async def obtener_por_correo(self, correo: str) -> Usuario | None:
        return self._usuarios.get(correo)

    async def listar_activos(self) -> list[Usuario]:
        return [usuario for usuario in self._usuarios.values() if usuario.activo]

    async def actualizar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.correo.valor] = usuario
