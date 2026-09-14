from modules.archivos.application.ports.file_storage import FileStoragePort
from modules.archivos.domain.entities.documento import Documento
from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from shared.uow import UnitOfWork


async def obtener_documentos(
    storage: FileStoragePort,
    repositorio: DocumentoRepository,
    uow: UnitOfWork,
) -> list[Documento]:
    async with uow:
        documentos = await repositorio.get_all()
        return documentos