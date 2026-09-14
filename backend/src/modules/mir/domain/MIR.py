from dataclasses import dataclass, field

import datetime

from modules.archivos.domain.entities.documento import Documento

@dataclass
class Mir:
    fecha_deteccion: datetime.date
    descripcion: str
    solucionado: bool
    archivo_adjunto: list[Documento]