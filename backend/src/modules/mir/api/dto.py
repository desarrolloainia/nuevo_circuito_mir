from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir


class CrearMirDTO(BaseModel):
    codigo_mir: str
    descripcion: str
    tipo: TipoMir
    detectada_por_id: UUID
    solucionado: bool
    prioridad: Prioridad | None = None
    solucion_adoptada: str | None = None
    analisis_causas: str | None = None
    algo_mas_que_hacer: str | None = None


class ActualizarMirDTO(BaseModel):
    descripcion: str | None = None
    tipo: TipoMir | None = None
    prioridad: Prioridad | None = None
    solucionado: bool | None = None
    solucion_adoptada: str | None = None
    analisis_causas: str | None = None
    algo_mas_que_hacer: str | None = None


class MirDTO(BaseModel):
    id: UUID
    codigo_mir: str
    descripcion: str
    tipo: TipoMir
    estado: Estado
    detectada_por_id: UUID
    solucionado: bool
    solucion_adoptada: str | None
    analisis_causas: str | None
    algo_mas_que_hacer: str | None
    prioridad: Prioridad | None
    tecnico_cld_id: UUID | None
    responsable_resolucion_id: UUID | None
    ejecutor_id: UUID | None
    fecha_prevista_resolucion: datetime | None
    fecha_comprobacion_eficacia: datetime | None
    resultado_comprobacion_eficacia: str | None
    documento_ids: list[UUID]
    creado_en: datetime
    modificado_en: datetime
    borrado: bool
    borrado_por_id: UUID | None
    borrado_en: datetime | None

    @classmethod
    def from_dominio(cls, mir: MIR) -> MirDTO:
        return cls(
            id=mir.id,
            codigo_mir=mir.codigo_mir,
            descripcion=mir.descripcion,
            tipo=mir.tipo,
            estado=mir.estado,
            detectada_por_id=mir.detectada_por_id,
            solucionado=mir.solucionado,
            solucion_adoptada=mir.solucion_adoptada,
            analisis_causas=mir.analisis_causas,
            algo_mas_que_hacer=mir.algo_mas_que_hacer,
            prioridad=mir.prioridad,
            tecnico_cld_id=mir.tecnico_cld_id,
            responsable_resolucion_id=mir.responsable_resolucion_id,
            ejecutor_id=mir.ejecutor_id,
            fecha_prevista_resolucion=mir.fecha_prevista_resolucion,
            fecha_comprobacion_eficacia=mir.fecha_comprobacion_eficacia,
            resultado_comprobacion_eficacia=mir.resultado_comprobacion_eficacia,
            documento_ids=[documento.id for documento in mir.documentos],
            creado_en=mir.creado_en,
            modificado_en=mir.modificado_en,
            borrado=mir.borrado,
            borrado_por_id=mir.borrado_por_id,
            borrado_en=mir.borrado_en,
        )
