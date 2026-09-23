from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.repository.mir_repository import MirRepository


async def obtener_por_codigo_mir(
    codigo_mir: str,
    mir_repositorio: MirRepository,
) -> MIR | None:
    """Obtiene un MIR por su código.

    Args:
        codigo_mir (str): Código del MIR a buscar.
        mir_repositorio (MirRepository): Repositorio de MIRs.

    Returns:
        MIR | None: El MIR encontrado o None si no existe.
    """
    return await mir_repositorio.get_by_codigo_mir(codigo_mir)
