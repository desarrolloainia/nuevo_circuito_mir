from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from modules.Documentos.domain.entities.documento import Documento
from modules.mir.domain.Enum.tipo import TipoMir
from src.modules.mir.domain.Enum.estado import Estado


@dataclass
class MIR:
    id: UUID

    codigo_mir: str

    descripcion: str
    tipo: TipoMir
    estado: Estado

    detectada_por_id: UUID

    solucionado: bool

    # Estos campos solo se usan si el estado es "resuelto"
    solucion_adoptada: str | None = None
    analisis_causas: str | None = None
    algo_mas_que_hacer: str | None = None

    tecnico_cld_id: UUID | None = None
    responsable_resolucion_id: UUID | None = None
    ejecutor_id: UUID | None = None

    fecha_prevista_resolucion: datetime | None = None

    fecha_comprobacion_eficacia: datetime | None = None
    resultado_comprobacion_eficacia: str | None = None

    documentos: list[Documento] = field(default_factory=list)

    creado_en: datetime = field(default_factory=datetime.now)
    modificado_en: datetime = field(default_factory=datetime.now)
