"""Actualizacion de los datos de registro de una MIR."""

import asyncio
from uuid import UUID, uuid4

import pytest

from modules.mir.application.uses_cases.actualizar_mir import actualizar_mir
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    DatoObligatorioFaltanteError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)


class MirRepositorioEnMemoria:
    def __init__(self, *mirs: MIR) -> None:
        self.mirs: dict[UUID, MIR] = {mir.id: mir for mir in mirs}
        self.actualizadas: list[MIR] = []

    async def get_by_id(self, mir_id: UUID) -> MIR | None:
        return self.mirs.get(mir_id)

    async def update_mir(self, mir: MIR) -> MIR:
        self.actualizadas.append(mir)
        return mir

    # El resto del puerto no interviene en la actualizacion.
    async def create_mir(self, mir: MIR) -> MIR:
        del mir
        raise NotImplementedError

    async def delete_mir(self, mir_id: UUID, actor_id: UUID) -> None:
        del mir_id, actor_id
        raise NotImplementedError

    async def get_mir_all(self) -> list[MIR]:
        raise NotImplementedError

    async def get_by_codigo_mir(self, codigo_mir: str) -> MIR | None:
        del codigo_mir
        raise NotImplementedError


def mir_ficticia(
    estado: Estado = Estado.EN_REVISION,
    solucionado: bool = False,
    solucion_adoptada: str | None = None,
    analisis_causas: str | None = None,
    algo_mas_que_hacer: str | None = None,
) -> MIR:
    return MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Se detecto una desviacion en el proceso.",
        tipo=TipoMir.INCIDENCIA,
        estado=estado,
        detectada_por_id=uuid4(),
        solucionado=solucionado,
        solucion_adoptada=solucion_adoptada,
        analisis_causas=analisis_causas,
        algo_mas_que_hacer=algo_mas_que_hacer,
    )


def test_una_mir_en_revision_actualiza_sus_datos_y_se_persiste():
    async def caso() -> None:
        mir = mir_ficticia()
        repo = MirRepositorioEnMemoria(mir)

        actualizada = await actualizar_mir(
            repo, mir.id, descripcion="Nueva descripcion.", tipo=TipoMir.MEJORA
        )

        assert actualizada.descripcion == "Nueva descripcion."
        assert actualizada.tipo == TipoMir.MEJORA
        assert repo.actualizadas == [actualizada]

    asyncio.run(caso())


def test_una_mir_inexistente_no_se_puede_actualizar():
    async def caso() -> None:
        with pytest.raises(MirNoEncontradaError):
            _ = await actualizar_mir(
                MirRepositorioEnMemoria(), uuid4(), descripcion="x"
            )

    asyncio.run(caso())


def test_una_mir_fuera_de_revision_no_es_editable():
    async def caso() -> None:
        mir = mir_ficticia(estado=Estado.EN_PROGRESO)
        repo = MirRepositorioEnMemoria(mir)

        with pytest.raises(EstadoInvalidoError):
            _ = await actualizar_mir(repo, mir.id, descripcion="Otra.")

        assert mir.descripcion == "Se detecto una desviacion en el proceso."
        assert repo.actualizadas == []

    asyncio.run(caso())


def test_una_descripcion_solo_con_espacios_se_rechaza():
    async def caso() -> None:
        mir = mir_ficticia()

        with pytest.raises(DatoObligatorioFaltanteError):
            _ = await actualizar_mir(
                MirRepositorioEnMemoria(mir), mir.id, descripcion="   "
            )

    asyncio.run(caso())


def test_marcar_solucionada_exige_los_tres_datos_de_solucion_sin_cambiar_nada():
    async def caso() -> None:
        mir = mir_ficticia()

        with pytest.raises(DatoObligatorioFaltanteError) as error:
            _ = await actualizar_mir(
                MirRepositorioEnMemoria(mir),
                mir.id,
                solucionado=True,
                solucion_adoptada="Se sustituyo el envase.",
            )

        assert "analisis_causas" in str(error.value)
        assert "algo_mas_que_hacer" in str(error.value)
        assert mir.solucionado is False
        assert mir.solucion_adoptada is None

    asyncio.run(caso())


def test_desmarcar_solucionada_descarta_los_datos_de_solucion():
    async def caso() -> None:
        mir = mir_ficticia(
            solucionado=True,
            solucion_adoptada="Solucion.",
            analisis_causas="Causa.",
            algo_mas_que_hacer="Nada.",
        )

        actualizada = await actualizar_mir(
            MirRepositorioEnMemoria(mir), mir.id, solucionado=False
        )

        assert actualizada.solucion_adoptada is None
        assert actualizada.analisis_causas is None
        assert actualizada.algo_mas_que_hacer is None

    asyncio.run(caso())
