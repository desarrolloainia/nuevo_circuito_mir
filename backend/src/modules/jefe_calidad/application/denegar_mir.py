import logging
from uuid import UUID

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.exceptions.exceptions import (
    ActorNoAutorizadoError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.mir.domain.repository.mir_repository import MirRepository
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


async def denegar_mir(
    mir_repo: MirRepository,
    usuario_repo: UsuarioRepository,
    mir_id: UUID,
    actor_id: UUID,
) -> MIR:
    """El jefe de CLD deniega una MIR que no procede. La transaccion la abre
    y confirma quien llama (el router)."""
    mir = await mir_repo.get_by_id(mir_id)
    if mir is None:
        logger.warning("Denegacion rechazada: MIR id=%s no encontrada", mir_id)
        raise MirNoEncontradaError(str(mir_id))

    actor = next(
        (usuario for usuario in await usuario_repo.listar_activos() if usuario.id == actor_id),
        None,
    )
    if actor is None:
        raise ActorNoAutorizadoError("Solo puede denegar la MIR el jefe de CLD")

    try:
        mir.comprobar_denegable(actor.rol)
    except (EstadoInvalidoError, ActorNoAutorizadoError) as error:
        logger.warning(
            "Denegacion rechazada: MIR %s (%s)", mir.codigo_mir, type(error).__name__
        )
        raise

    denegada = await mir_repo.editar_estado(mir.id, Estado.RECHAZADA)
    logger.info("MIR %s denegada por id=%s", denegada.codigo_mir, actor_id)
    return denegada
