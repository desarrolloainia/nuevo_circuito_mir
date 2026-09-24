from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID

from modules.archivos.domain.entities.documento import Documento
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.prioridad import Prioridad
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    ActorNoAutorizadoError,
    DatoObligatorioFaltanteError,
    EstadoInvalidoError,
)
from modules.usuarios.domain.Enum.rol import Rol


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

    prioridad: Prioridad | None = None

    tecnico_cld_id: UUID | None = None
    responsable_resolucion_id: UUID | None = None
    ejecutor_id: UUID | None = None

    fecha_prevista_resolucion: datetime | None = None

    fecha_comprobacion_eficacia: datetime | None = None
    resultado_comprobacion_eficacia: str | None = None

    documentos: list[Documento] = field(default_factory=list)

    fecha_deteccion: date | None = None
    empresa_nombre: str | None = None
    persona_contacto: str | None = None
    telefono: str | None = None
    correo_electronico: str | None = None
    nombre_comercial: str | None = None
    codigo_cliente: str | None = None

    creado_en: datetime = field(default_factory=datetime.now)
    modificado_en: datetime = field(default_factory=datetime.now)
    borrado: bool = False
    borrado_por_id: UUID | None = None
    borrado_en: datetime | None = None

    def __post_init__(self) -> None:
        if not self.descripcion.strip():
            raise DatoObligatorioFaltanteError("descripcion")
        if self.solucionado:
            solucion = (
                self.solucion_adoptada,
                self.analisis_causas,
                self.algo_mas_que_hacer,
            )
            if any(not valor or not valor.strip() for valor in solucion):
                raise DatoObligatorioFaltanteError("datos de solucion")

    def dar_de_baja(self, actor_id: UUID) -> None:
        if self.borrado:
            raise EstadoInvalidoError("La MIR ya esta dada de baja")
        ahora = datetime.now(UTC)
        self.borrado = True
        self.borrado_por_id = actor_id
        self.borrado_en = ahora
        self.modificado_en = ahora

    def asignar_tecnico_cld(self, tecnico_cld_id: UUID) -> None:
        if self.borrado or self.estado != Estado.EN_REVISION:
            raise EstadoInvalidoError("Solo se asigna un tecnico a una MIR en revision")
        self.tecnico_cld_id = tecnico_cld_id
        self.estado = Estado.EN_PROGRESO
        self.modificado_en = datetime.now(UTC)

    def comprobar_denegable(self, rol: Rol) -> None:
        """La MIR no procede (PG09, etapa 3)."""

        if self.borrado or self.estado != Estado.EN_REVISION:
            raise EstadoInvalidoError("Solo se deniega una MIR en revisión")

        if rol != Rol.JEFE_CLD:
            raise ActorNoAutorizadoError("Solo puede denegar la MIR el jefe de CLD")

    def actualizar(
        self,
        *,
        descripcion: str | None = None,
        tipo: TipoMir | None = None,
        prioridad: Prioridad | None = None,
        solucionado: bool | None = None,
        solucion_adoptada: str | None = None,
        analisis_causas: str | None = None,
        algo_mas_que_hacer: str | None = None,
    ) -> None:
        if self.borrado or self.estado != Estado.EN_REVISION:
            raise EstadoInvalidoError("La MIR no es editable")

        nueva_descripcion = (
            self.descripcion if descripcion is None else descripcion.strip()
        )
        if not nueva_descripcion:
            raise DatoObligatorioFaltanteError("descripcion")
        nuevo_solucionado = self.solucionado if solucionado is None else solucionado
        solucion = {
            "solucion_adoptada": self.solucion_adoptada
            if solucion_adoptada is None
            else solucion_adoptada.strip(),
            "analisis_causas": self.analisis_causas
            if analisis_causas is None
            else analisis_causas.strip(),
            "algo_mas_que_hacer": self.algo_mas_que_hacer
            if algo_mas_que_hacer is None
            else algo_mas_que_hacer.strip(),
        }
        if nuevo_solucionado:
            faltantes = [campo for campo, valor in solucion.items() if not valor]
            if faltantes:
                raise DatoObligatorioFaltanteError(", ".join(faltantes))
        else:
            solucion = dict.fromkeys(solucion)

        self.descripcion = nueva_descripcion
        self.tipo = tipo or self.tipo
        self.prioridad = prioridad or self.prioridad
        self.solucionado = nuevo_solucionado
        self.solucion_adoptada = solucion["solucion_adoptada"]
        self.analisis_causas = solucion["analisis_causas"]
        self.algo_mas_que_hacer = solucion["algo_mas_que_hacer"]
