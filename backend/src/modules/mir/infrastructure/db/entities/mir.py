import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Table, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.archivos.infrastructure.db.entities.documento import DocumentoORM
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir
from shared.database import Base

mir_documentos = Table(
    "mir_documentos",
    Base.metadata,
    Column(
        "mir_id",
        UUID(as_uuid=True),
        ForeignKey("mirs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "documento_id",
        UUID(as_uuid=True),
        ForeignKey("documentos.id", ondelete="RESTRICT"),
        primary_key=True,
        unique=True,
    ),
)


class MirOrm(Base):
    __tablename__ = "mirs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    codigo_mir: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)

    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoMir] = mapped_column(
        SqlEnum(TipoMir, name="tipo_mir"), nullable=False
    )
    estado: Mapped[Estado] = mapped_column(
        SqlEnum(Estado, name="estado_mir"), nullable=False
    )

    detectada_por_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    solucionado: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Solo se rellenan si solucionado es True
    solucion_adoptada: Mapped[str | None] = mapped_column(Text, nullable=True)
    analisis_causas: Mapped[str | None] = mapped_column(Text, nullable=True)
    algo_mas_que_hacer: Mapped[str | None] = mapped_column(Text, nullable=True)

    prioridad: Mapped[Prioridad | None] = mapped_column(
        SqlEnum(Prioridad, name="prioridad_mir"), nullable=True
    )

    tecnico_cld_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    responsable_resolucion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    ejecutor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    fecha_prevista_resolucion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    fecha_comprobacion_eficacia: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resultado_comprobacion_eficacia: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    archivos_adjuntos: Mapped[list[DocumentoORM]] = relationship(
        secondary=mir_documentos,
        lazy="selectin",
        passive_deletes=True,
    )

    fecha_deteccion: Mapped[date | None] = mapped_column(Date, nullable=True)
    empresa_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    persona_contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(50), nullable=True)
    correo_electronico: Mapped[str | None] = mapped_column(String(320), nullable=True)
    nombre_comercial: Mapped[str | None] = mapped_column(String(255), nullable=True)
    codigo_cliente: Mapped[str | None] = mapped_column(String(100), nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    modificado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    borrado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    borrado_por_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    borrado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
