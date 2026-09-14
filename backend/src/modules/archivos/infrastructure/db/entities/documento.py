import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from shared.database import Base


class DocumentoORM(Base):
    __tablename__ = "documentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(nullable=False)
    tipo: Mapped[TipoDocumento] = mapped_column(
        SqlEnum(TipoDocumento, name="tipo_documento"), nullable=False
    )
    storage_id: Mapped[str] = mapped_column(nullable=False)
    creado_por: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
