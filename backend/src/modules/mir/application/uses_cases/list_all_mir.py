from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.repository.mir_repository import MirRepository


async def list_all_mir(
    mir_repositorio: MirRepository,
) -> list[MIR]:
    """Obtiene todos los MIRs.

    Args:
        mir_repositorio (MirRepository): Repositorio de MIRs.

    Returns:
        list[MIR]: Lista de todos los MIRs.
    """
    return await mir_repositorio.get_mir_all()
