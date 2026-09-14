import logging
from uuid import UUID

from modules.archivos.application.ports.file_storage import (
    FileStorageNotFoundError,
    FileStoragePort,
)
from modules.archivos.domain.entities.documento import Documento
from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from shared.uow import UnitOfWork

logger = logging.getLogger(__name__)


async def editar_documento(
    *,
    documento_id: UUID,
    storage: FileStoragePort,
    repositorio: DocumentoRepository,
    uow: UnitOfWork,
    nombre: str | None = None,
    contenido: bytes | None = None,
    content_type: str | None = None,
    tipo: TipoDocumento | None = None,
) -> Documento | None:
    """Edita los metadatos o sustituye el archivo de un documento."""

    subido = None
    storage_id_anterior: str | None = None

    try:
        async with uow:
            documento = await repositorio.get_by_id(documento_id)

            if documento is None:
                return None

            if contenido is None:
                if nombre is not None:
                    documento.nombre = nombre

                if tipo is not None:
                    documento.tipo = tipo

                documento = await repositorio.update(documento)
                await uow.commit()

                return documento

            if nombre is None or content_type is None:
                raise ValueError(
                    "nombre y content_type deben proporcionarse al sustituir el archivo"
                )

            # El archivo anterior se conserva hasta confirmar la actualización.
            storage_id_anterior = documento.storage_id

            subido = await storage.subir(
                nombre,
                contenido,
                content_type,
            )

            documento.nombre = subido.nombre
            documento.storage_id = subido.storage_id

            if tipo is not None:
                documento.tipo = tipo

            documento = await repositorio.update(documento)
            await uow.commit()


    ##Codigo para evitar dejar archivos huérfanos en caso de error al actualizar el documento
    except Exception:
        # Evita dejar un archivo huérfano si falla la actualización.
        if subido is not None:
            try:
                await storage.eliminar(subido.storage_id)
            except Exception:
                logger.exception(
                    "No se pudo revertir archivo nuevo storage_id=%s",
                    subido.storage_id,
                )

        raise

    # Elimina el archivo anterior si se ha actualizado correctamente.
    if storage_id_anterior is not None:
        try:
            await storage.eliminar(storage_id_anterior)
        except FileStorageNotFoundError:
            pass
        except Exception:
            logger.exception(
                "No se pudo eliminar archivo sustituido storage_id=%s",
                storage_id_anterior,
            )

    return documento
