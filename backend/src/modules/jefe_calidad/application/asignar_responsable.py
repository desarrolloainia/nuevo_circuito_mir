import logging
from uuid import UUID

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.exceptions.exceptions import MirNoEncontradaError
from modules.mir.domain.repository.mir_repository import MirRepository
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from modules.usuarios.domain.repository.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


class UsuarioNoEsTecnicoCldError(Exception):
    """El usuario designado no tiene el rol de tecnico de CLD."""


async def asignar_responsable(
    mir_repo: MirRepository,
    usuario_repo: UsuarioRepository,
    mir_id: UUID,
    tecnico_cld_id: UUID,
) -> MIR:
    """El jefe de CLD designa al tecnico de CLD que gestiona la MIR. La
    transaccion la abre y confirma quien llama (el router)."""
    mir = await mir_repo.get_by_id(mir_id)
    if mir is None:
        logger.warning("Asignacion rechazada: MIR id=%s no encontrada", mir_id)
        raise MirNoEncontradaError(str(mir_id))

    # ponytail: busqueda lineal sobre los activos; anadir obtener_por_id al
    # puerto si la plantilla crece.
    tecnico = next(
        (u for u in await usuario_repo.listar_activos() if u.id == tecnico_cld_id),
        None,
    )
    if tecnico is None:
        logger.warning("Asignacion rechazada: usuario id=%s no activo", tecnico_cld_id)
        raise UsuarioNoEncontradoError(str(tecnico_cld_id))
    if tecnico.rol != Rol.TECNICO_CLD:
        logger.warning(
            "Asignacion rechazada: usuario id=%s con rol %s", tecnico.id, tecnico.rol
        )
        raise UsuarioNoEsTecnicoCldError(str(tecnico.id))

    mir.asignar_tecnico_cld(tecnico.id)
    asignada = await mir_repo.update_mir(mir)
    logger.info("MIR %s asignada al tecnico id=%s", asignada.codigo_mir, tecnico.id)
    return asignada
