import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from modules.mir.application.uses_cases.delete_mir import delete_mir
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    EstadoInvalidoError,
    MirNoEncontradaError,
)


def mir_ficticia() -> MIR:
    return MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Incidencia ficticia",
        tipo=TipoMir.INCIDENCIA,
        estado=Estado.EN_REVISION,
        detectada_por_id=uuid4(),
        solucionado=False,
    )


class RepositorioFalso:
    def __init__(self, mir: MIR | None) -> None:
        self.mir: MIR | None = mir
        self.guardadas: list[MIR] = []

    async def get_by_id(self, mir_id: UUID) -> MIR | None:
        return self.mir if self.mir and self.mir.id == mir_id else None

    async def delete_mir(self, mir_id: UUID, actor_id: UUID) -> None:
        del mir_id, actor_id
        raise AssertionError("No se debe borrar fisicamente")

    async def update_mir(self, mir: MIR) -> MIR:
        self.guardadas.append(mir)
        return mir

    async def create_mir(self, mir: MIR) -> MIR:
        return mir

    async def get_mir_all(self) -> list[MIR]:
        return [self.mir] if self.mir is not None else []

    async def get_by_codigo_mir(self, codigo_mir: str) -> MIR | None:
        return self.mir if self.mir and self.mir.codigo_mir == codigo_mir else None


def test_la_baja_marca_la_mir_y_conserva_actor_y_fecha() -> None:
    mir = mir_ficticia()
    actor = uuid4()
    repo = RepositorioFalso(mir)

    asyncio.run(delete_mir(mir.id, repo, actor_id=actor))

    assert mir.borrado is True
    assert mir.borrado_por_id == actor
    assert mir.borrado_en is not None
    assert mir.borrado_en <= datetime.now(UTC)
    assert repo.guardadas == [mir]


def test_no_se_puede_dar_de_baja_dos_veces() -> None:
    mir = mir_ficticia()
    mir.dar_de_baja(uuid4())
    with pytest.raises(EstadoInvalidoError):
        asyncio.run(delete_mir(mir.id, RepositorioFalso(mir), actor_id=uuid4()))


def test_la_baja_de_una_mir_inexistente_responde_con_error_de_dominio() -> None:
    with pytest.raises(MirNoEncontradaError):
        asyncio.run(delete_mir(uuid4(), RepositorioFalso(None), actor_id=uuid4()))
