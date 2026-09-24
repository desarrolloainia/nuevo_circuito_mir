"""El jefe de CLD solo ve las MIR pendientes de revision."""

import asyncio

from modules.jefe_calidad.application.listar_mir_en_revision import (
    listar_mir_en_revision,
)
from modules.mir.domain.Enum.estado import Estado
from tests.unit.jefe_calidad.test_denegar_mir import mir_ficticia
from tests.unit.mir.test_actualizar_mir import MirRepositorioEnMemoria


def test_solo_se_listan_las_mir_en_revision():
    async def caso() -> None:
        en_revision = mir_ficticia()
        en_progreso = mir_ficticia(estado=Estado.EN_PROGRESO)
        rechazada = mir_ficticia(estado=Estado.RECHAZADA)
        repo = MirRepositorioEnMemoria(en_revision, en_progreso, rechazada)

        assert await listar_mir_en_revision(repo) == [en_revision]

    asyncio.run(caso())
