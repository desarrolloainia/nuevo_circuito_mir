from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator

from modules.archivos.domain.Enum.estado_documetno import TipoDocumento
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir


class CrearMirDTO(BaseModel):
    descripcion: str
    tipo: TipoMir
    fecha_deteccion: date
    detectada_por_id: UUID
    solucionado: bool
    # Solo aplica si solucionado es True
    solucion_adoptada: str | None = None
    analisis_causas: str | None = None
    algo_mas_que_hacer: str | None = None
    prioridad: Prioridad | None = None
    tipos_documento: list[TipoDocumento] = Field(default_factory=list)
    empresa_nombre: str = Field(min_length=1, max_length=255)
    persona_contacto: str = Field(min_length=1, max_length=255)
    telefono: str = Field(min_length=1, max_length=50)
    correo_electronico: str = Field(
        min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    )
    nombre_comercial: str | None = None
    codigo_cliente: str | None = None

    @field_validator("fecha_deteccion")
    @classmethod
    def fecha_no_futura(cls, valor: date) -> date:
        if valor > datetime.now(ZoneInfo("Europe/Madrid")).date():
            raise ValueError("La fecha de deteccion no puede ser futura")
        return valor

    @field_validator("descripcion", "empresa_nombre", "persona_contacto", "telefono")
    @classmethod
    def no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("Este campo es obligatorio")
        return valor.strip()


class ActualizarMirDTO(BaseModel):
    descripcion: str | None = None
    tipo: TipoMir | None = None
    prioridad: Prioridad | None = None
    solucionado: bool | None = None
    solucion_adoptada: str | None = None
    analisis_causas: str | None = None
    algo_mas_que_hacer: str | None = None


class AsignarTecnicoCldDTO(BaseModel):
    tecnico_cld_id: UUID


class DenegarMirDTO(BaseModel):
    actor_id: UUID


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
    fecha_deteccion: date | None
    empresa_nombre: str | None
    persona_contacto: str | None
    telefono: str | None
    correo_electronico: str | None
    nombre_comercial: str | None
    codigo_cliente: str | None
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
            fecha_deteccion=mir.fecha_deteccion,
            empresa_nombre=mir.empresa_nombre,
            persona_contacto=mir.persona_contacto,
            telefono=mir.telefono,
            correo_electronico=mir.correo_electronico,
            nombre_comercial=mir.nombre_comercial,
            codigo_cliente=mir.codigo_cliente,
            creado_en=mir.creado_en,
            modificado_en=mir.modificado_en,
            borrado=mir.borrado,
            borrado_por_id=mir.borrado_por_id,
            borrado_en=mir.borrado_en,
        )
