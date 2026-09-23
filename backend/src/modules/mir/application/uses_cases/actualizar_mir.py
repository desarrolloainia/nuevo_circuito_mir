import logging
from uuid import UUID

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    DatoObligatorioFaltanteError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.mir.domain.repository.mir_repository import MirRepository

logger = logging.getLogger(__name__)


async def actualizar_mir(
    repo: MirRepository,
    mir_id: UUID,
    *,
    descripcion: str | None = None,
    tipo: TipoMir | None = None,
    prioridad: Prioridad | None = None,
    solucionado: bool | None = None,
    solucion_adoptada: str | None = None,
    analisis_causas: str | None = None,
    algo_mas_que_hacer: str | None = None,
) -> MIR:
    """Actualiza los datos de registro de una MIR. La transaccion la abre y
    confirma quien llama (el router), como en el modulo de usuarios."""
    mir = await repo.get_by_id(mir_id)
    if mir is None:
        logger.warning("Actualizacion rechazada: MIR id=%s no encontrada", mir_id)
        raise MirNoEncontradaError(str(mir_id))

    # Solo se registran identificadores y nombres de campo: nunca contenido de
    # la MIR, que puede llevar datos personales (AGENTS.md §10).
    try:
        mir.actualizar(
            descripcion=descripcion,
            tipo=tipo,
            prioridad=prioridad,
            solucionado=solucionado,
            solucion_adoptada=solucion_adoptada,
            analisis_causas=analisis_causas,
            algo_mas_que_hacer=algo_mas_que_hacer,
        )
    except EstadoInvalidoError:
        logger.warning(
            "Actualizacion rechazada: MIR %s en estado %s", mir.codigo_mir, mir.estado
        )
        raise
    except DatoObligatorioFaltanteError as error:
        logger.warning(
            "Actualizacion rechazada: MIR %s sin datos obligatorios (%s)",
            mir.codigo_mir,
            error,
        )
        raise

    actualizada = await repo.update_mir(mir)
    logger.info("MIR %s actualizada", actualizada.codigo_mir)
    return actualizada
