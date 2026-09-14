from uuid import UUID

from sqlalchemy import select

from modules.archivos.domain.entities.documento import Documento
from modules.archivos.infrastructure.db.entities.documento import DocumentoORM
from shared.uow import UnitOfWork


def to_domain(documento_orm: DocumentoORM) -> Documento:
    """Convierte una entidad ORM en una entidad de dominio.

    Mantiene desacoplada la capa de persistencia de la capa de dominio,
    evitando que el dominio dependa directamente de SQLAlchemy.
    """
    return Documento(
        id=documento_orm.id,
        nombre=documento_orm.nombre,
        tipo=documento_orm.tipo,
        storage_id=documento_orm.storage_id,
        creado_por=documento_orm.creado_por,
        creado_en=documento_orm.creado_en,
    )


def to_orm(documento: Documento) -> DocumentoORM:
    """Convierte una entidad de dominio en una entidad ORM.

    Transforma el modelo de dominio al modelo utilizado por
    infraestructura para persistirlo en base de datos.
    """
    return DocumentoORM(
        id=documento.id,
        nombre=documento.nombre,
        tipo=documento.tipo,
        storage_id=documento.storage_id,
        creado_por=documento.creado_por,
        creado_en=documento.creado_en,
    )


class DocumentoRepositorySqlAlchemy:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def save(self, documento: Documento) -> Documento:
        """Guarda un documento en la base de datos.

        Args:
            documento (Documento): Documento a guardar.

        Returns:
            Documento: Documento guardado.
        """
        documento_orm = to_orm(documento)
        self.uow.session.add(documento_orm)
        await self.uow.session.flush()
        return documento

    async def update(self, documento: Documento) -> Documento:
        """Actualiza los metadatos de un documento sin confirmar la transacción."""

        documento_orm = await self.uow.session.get(DocumentoORM, documento.id)
        if documento_orm is None:
            raise ValueError(f"Documento con id {documento.id} no encontrado")

        documento_orm.nombre = documento.nombre
        documento_orm.tipo = documento.tipo
        documento_orm.storage_id = documento.storage_id
        documento_orm.creado_por = documento.creado_por
        return documento

    async def delete(self, documento_id: UUID) -> None:
        """Elimina un documento por su identificador."""

        documento_orm = await self.uow.session.get(DocumentoORM, documento_id)

        if documento_orm is not None:
            await self.uow.session.delete(documento_orm)

    async def get_by_id(self, documento_id: UUID) -> Documento | None:
        """Obtiene un documento por su identificador."""

        result = await self.uow.session.execute(
            select(DocumentoORM).where(DocumentoORM.id == documento_id)
        )
        documento_orm = result.scalar_one_or_none()
        return to_domain(documento_orm) if documento_orm else None

    async def get_all(self) -> list[Documento]:
        """Obtiene todos los documentos de la base de datos."""

        result = await self.uow.session.execute(select(DocumentoORM))

        return [to_domain(documento) for documento in result.scalars().all()]
