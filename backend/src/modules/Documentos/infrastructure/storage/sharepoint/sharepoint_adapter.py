from kiota_abstractions.api_error import APIError

from ....application.ports.file_storage import (
    ArchivoSubido,
    FileStorageAuthError,
    FileStorageError,
    FileStorageNotFoundError,
    FileStoragePort,
    FileStorageRateLimitedError,
)
from .graph_client import SharePointGraphClient
from .schema import DriveItemSchema, GraphErrorDetail


class SharePointFileStorageAdapter(FileStoragePort):
    """Implementa el puerto de storage de archivos contra SharePoint via Microsoft Graph."""

    def __init__(self, client: SharePointGraphClient) -> None:
        self._client = client

    async def subir(self, nombre: str, contenido: bytes, content_type: str) -> ArchivoSubido:
        try:
            drive_item = await self._client.upload_content(nombre, contenido, content_type)
        except APIError as error:
            raise self._traducir_error(error) from error

        item = DriveItemSchema.model_validate(drive_item)
        return ArchivoSubido(
            storage_id=item.id,
            nombre=item.name or nombre,
            tamano_bytes=item.size if item.size is not None else len(contenido),
            url=item.web_url,
        )

    async def eliminar(self, storage_id: str) -> None:
        try:
            await self._client.delete_item(storage_id)
        except APIError as error:
            raise self._traducir_error(error) from error

    async def descargar(self, storage_id: str) -> bytes:
        try:
            return await self._client.download_content(storage_id)
        except APIError as error:
            raise self._traducir_error(error) from error

    @staticmethod
    def _traducir_error(error: APIError) -> FileStorageError:
        detalle = getattr(error, "error", None)
        mensaje = (
            GraphErrorDetail.model_validate(detalle, from_attributes=True).message
            if detalle is not None
            else error.message
        )
        status = error.response_status_code

        if status == 404:
            return FileStorageNotFoundError(mensaje or "Archivo no encontrado en SharePoint")
        if status in (401, 403):
            return FileStorageAuthError(mensaje or "Fallo de autenticacion contra SharePoint")
        if status == 429:
            return FileStorageRateLimitedError(
                mensaje or "SharePoint ha aplicado throttling a la peticion"
            )
        return FileStorageError(mensaje or "Error al operar contra SharePoint")
