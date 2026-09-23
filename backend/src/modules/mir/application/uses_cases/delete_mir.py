from uuid import UUID

from modules.mir.domain.exceptions.exceptions import MirNoEncontradaError
from modules.mir.domain.repository.mir_repository import MirRepository


async def delete_mir(
    mir_id: UUID,
    mir_repositorio: MirRepository,
    *,
    actor_id: UUID,
) -> None:
    mir = await mir_repositorio.get_by_id(mir_id)
    if mir is None:
        raise MirNoEncontradaError("MIR no encontrada")
    mir.dar_de_baja(actor_id)
    _ = await mir_repositorio.update_mir(mir)
