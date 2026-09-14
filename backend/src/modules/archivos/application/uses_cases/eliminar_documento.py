import logging
from uuid import UUID

from modules.archivos.application.ports.file_storage import (
    FileStorageNotFoundError,
    FileStoragePort,
)
from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from shared.uow import UnitOfWork

logger = logging.getLogger(__name__)

async def eliminar_documento(
    documento_id: UUID,
    storage: FileStoragePort,
    repositorio: DocumentoRepository,
    uow: UnitOfWork,
) -> None:
    async with uow:
        documento = await repositorio.get_by_id(documento_id)
        if documento is None:
            return logger.error(f"Documento con ID {documento_id} no encontrado para eliminar.")

        try:
            await storage.eliminar(documento.storage_id)
        except FileStorageNotFoundError:
            pass

        await repositorio.delete(documento_id)
        await uow.commit()
        logger.info(f"Documento con ID {documento_id} eliminado correctamente.")
