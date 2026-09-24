from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.repository.mir_repository import MirRepository


async def listar_mir_en_revision(mir_repo: MirRepository) -> list[MIR]:
    """El jefe de CLD solo trabaja con las MIR pendientes de revision."""
    return await mir_repo.filtrar_estado(Estado.EN_REVISION)
