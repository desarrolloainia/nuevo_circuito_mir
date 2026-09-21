from mimetypes import guess_type
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from modules.Documentos.api.dto import DocumentoDTO
from modules.Documentos.application.ports.file_storage import (
    FileStorageNotFoundError,
    FileStoragePort,
)
from modules.Documentos.application.uses_cases.obtener_documentos import (
    obtener_documentos,
)
from modules.Documentos.infrastructure.db.persistence.documento_repository import (
    DocumentoRepositorySqlAlchemy,
)
from modules.Documentos.infrastructure.storage.sharepoint.graph_client import (
    SharePointGraphClient,
)
from modules.Documentos.infrastructure.storage.sharepoint.schema import (
    SharePointSettings,
)
from modules.Documentos.infrastructure.storage.sharepoint.sharepoint_adapter import (
    SharePointFileStorageAdapter,
)
from shared.uow import UnitOfWork

router = APIRouter(prefix="/archivos", tags=["Archivos"])


def get_uow() -> UnitOfWork:
    return UnitOfWork()


def get_storage() -> FileStoragePort:
    return SharePointFileStorageAdapter(SharePointGraphClient(SharePointSettings()))  # pyright: ignore[reportCallIssue]


def error_http(error: Exception) -> HTTPException:
    return HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))


@router.get("/", response_model=list[DocumentoDTO])
async def listar_archivos(
    uow: UnitOfWork = Depends(get_uow),
    storage: FileStoragePort = Depends(get_storage),
):
    try:
        documentos = await obtener_documentos(
            storage=storage,
            repositorio=DocumentoRepositorySqlAlchemy(uow),
            uow=uow,
        )
    except Exception as error:
        raise error_http(error) from error
    return documentos


@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_archivo(
    documento_id: str,
    uow: UnitOfWork = Depends(get_uow),
    storage: FileStoragePort = Depends(get_storage),
):
    from modules.Documentos.application.uses_cases.eliminar_documento import (
        eliminar_documento,
    )

    try:
        await eliminar_documento(
            documento_id=UUID(documento_id),
            storage=storage,
            repositorio=DocumentoRepositorySqlAlchemy(uow),
            uow=uow,
        )
    except Exception as error:
        raise error_http(error) from error


@router.get("/{documento_id}/contenido")
async def obtener_contenido_archivo(
    documento_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
    storage: FileStoragePort = Depends(get_storage),
) -> Response:
    try:
        async with uow:
            documento = await DocumentoRepositorySqlAlchemy(uow).get_by_id(documento_id)
        if documento is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
        contenido = await storage.descargar(documento.storage_id)
    except HTTPException:
        raise
    except FileStorageNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Archivo no encontrado"
        ) from error
    except Exception as error:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "No se ha podido leer el archivo"
        ) from error

    return Response(
        content=contenido,
        media_type=guess_type(documento.nombre)[0] or "application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''"
            + quote(documento.nombre, safe=""),
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
            "Content-Security-Policy": "sandbox",
        },
    )
