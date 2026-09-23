"""Dobles escritos a mano para los puertos del registro de MIR."""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.mir.domain.entities.mir import MIR


class RelojFijo:
    """Devuelve siempre el mismo instante UTC."""

    def __init__(self, instante: datetime) -> None:
        self.instante = instante

    def __call__(self) -> datetime:
        return self.instante


class ConsultaDetectoresFalsa:
    def __init__(self, existentes: Sequence[UUID] = ()) -> None:
        self.existentes: set[UUID] = set(existentes)
        self.consultas: list[UUID] = []

    async def existe(self, detector_id: UUID) -> bool:
        self.consultas.append(detector_id)
        return detector_id in self.existentes


class VinculoDocumentosFalso:
    def __init__(self, documentos: dict[UUID, UUID | None] | None = None) -> None:
        self.documentos: dict[UUID, UUID | None] = dict(documentos or {})
        self.bloqueados: list[list[UUID]] = []
        self.vinculados: list[tuple[list[UUID], UUID]] = []

    async def bloquear(self, documento_ids: Sequence[UUID]) -> dict[UUID, UUID | None]:
        self.bloqueados.append(list(documento_ids))
        return {
            documento_id: self.documentos[documento_id]
            for documento_id in documento_ids
            if documento_id in self.documentos
        }

    async def vincular(self, documento_ids: Sequence[UUID], mir_id: UUID) -> None:
        self.vinculados.append((list(documento_ids), mir_id))
        for documento_id in documento_ids:
            self.documentos[documento_id] = mir_id


class MirRepositorioFalso:
    """Reserva numeros en memoria y guarda las MIR confirmadas por el caso de uso."""

    def __init__(self, fallar_al_guardar: bool = False) -> None:
        self.contadores: dict[int, int] = {}
        self.reservas: list[int] = []
        self.guardadas: list[MIR] = []
        self.fallar_al_guardar = fallar_al_guardar

    async def reservar_numero(self, anio: int) -> int:
        numero = self.contadores.get(anio, 0) + 1
        self.contadores[anio] = numero
        self.reservas.append(anio)
        return numero

    async def guardar(self, mir: MIR) -> MIR:
        if self.fallar_al_guardar:
            raise RuntimeError("fallo simulado de persistencia")
        self.guardadas.append(mir)
        return mir


class UnidadTrabajoFalsa:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


def instante(anio: int, mes: int, dia: int, hora: int = 9) -> datetime:
    return datetime(anio, mes, dia, hora, tzinfo=UTC)


def detector_existente() -> tuple[UUID, ConsultaDetectoresFalsa]:
    detector_id = uuid4()
    return detector_id, ConsultaDetectoresFalsa([detector_id])
