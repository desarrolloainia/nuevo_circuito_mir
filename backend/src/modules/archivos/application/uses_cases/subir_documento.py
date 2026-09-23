import logging
from uuid import UUID

from modules.archivos.application.ports.file_storage import FileStoragePort
from modules.archivos.domain.entities.documento import Documento
from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from shared.uow import UnitOfWork

logger = logging.getLogger(__name__)


async def subir_documento(
    *,
    nombre: str,
    contenido: bytes,
    content_type: str,
    tipo: TipoDocumento,
    creado_por: UUID,
    storage: FileStoragePort,
    repositorio: DocumentoRepository,
    uow: UnitOfWork,
    gestionar_transaccion: bool = True,
) -> Documento:
    """Sube el archivo a storage y persiste el Documento resultante.

    Si falla el guardado en BD tras subir el archivo, intenta borrarlo de
    storage para no dejarlo huérfano (best-effort, no es un 2PC real).
    """
    subido = await storage.subir(nombre, contenido, content_type)

    documento = Documento(
        nombre=subido.nombre,
        tipo=tipo,
        storage_id=subido.storage_id,
        creado_por=creado_por,
    )

    async def guardar() -> Documento:
        if gestionar_transaccion:
            async with uow:
                resultado = await repositorio.save(documento)
                await uow.commit()
                return resultado
        return await repositorio.save(documento)

    try:
        return await guardar()
    except Exception:
        logger.exception(
            "Fallo al guardar Documento tras subir %s (storage_id=%s); revirtiendo archivo",
            nombre,
            subido.storage_id,
        )
        try:
            await storage.eliminar(subido.storage_id)
        except Exception:
            logger.exception(
                "No se pudo revertir archivo huérfano storage_id=%s", subido.storage_id
            )
        raise
