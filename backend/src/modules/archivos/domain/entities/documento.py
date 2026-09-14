from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.archivos.domain.Enum.estado_documetno import TipoDocumento


@dataclass
class Documento:
    nombre: str
    tipo: TipoDocumento
    storage_id: str
    creado_por: UUID
    id: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
