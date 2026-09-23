import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from modules.archivos.application.ports.file_storage import FileStoragePort
from modules.archivos.application.uses_cases.subir_documento import subir_documento
from modules.archivos.domain.entities.documento import Documento
from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from modules.archivos.domain.repository.documento_repository import DocumentoRepository
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.repository.mir_repository import MirRepository
from shared.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdjuntoMir:
    nombre: str
    contenido: bytes
    content_type: str
    tipo: TipoDocumento


async def crear_mir_con_archivos(
    *,
    codigo_mir: str,
    descripcion: str,
    tipo: TipoMir,
    detectada_por_id: UUID,
    solucionado: bool,
    adjuntos: list[AdjuntoMir],
    storage: FileStoragePort | None,
    documento_repositorio: DocumentoRepository,
    mir_repositorio: MirRepository,
    uow: UnitOfWork,
    prioridad: Prioridad | None = None,
    solucion_adoptada: str | None = None,
    analisis_causas: str | None = None,
    algo_mas_que_hacer: str | None = None,
) -> MIR:
    if adjuntos and storage is None:
        raise ValueError("Se requiere almacenamiento para los adjuntos")
    documentos: list[Documento] = []
    try:
        async with uow:
            for adjunto in adjuntos:
                assert storage is not None
                documentos.append(
                    await subir_documento(
                        nombre=adjunto.nombre,
                        contenido=adjunto.contenido,
                        content_type=adjunto.content_type,
                        tipo=adjunto.tipo,
                        creado_por=detectada_por_id,
                        storage=storage,
                        repositorio=documento_repositorio,
                        uow=uow,
                        gestionar_transaccion=False,
                    )
                )

            mir = MIR(
                id=uuid4(),
                codigo_mir=codigo_mir,
                descripcion=descripcion,
                tipo=tipo,
                estado=Estado.EN_REVISION,
                detectada_por_id=detectada_por_id,
                solucionado=solucionado,
                prioridad=prioridad,
                solucion_adoptada=solucion_adoptada,
                analisis_causas=analisis_causas,
                algo_mas_que_hacer=algo_mas_que_hacer,
                documentos=documentos,
            )
            _ = await mir_repositorio.create_mir(mir)
            await uow.commit()
            logger.info("MIR creada con id=%s y codigo_mir=%s", mir.id, mir.codigo_mir)
            return mir
    except Exception:
        logger.exception("Error al crear MIR")
        for documento in reversed(documentos):
            try:
                assert storage is not None
                await storage.eliminar(documento.storage_id)
            except Exception:
                logger.exception(
                    "No se pudo compensar storage_id=%s", documento.storage_id
                )
        raise
