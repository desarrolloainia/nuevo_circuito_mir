from collections.abc import Iterator
from typing import Self
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.mir.api import router as modulo_router
from modules.mir.domain.entities.mir import MIR


class UnidadFalsa:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def commit(self) -> None:
        return None


class RepoFalso:
    def __init__(self) -> None:
        self.mirs: dict[UUID, MIR] = {}

    async def create_mir(self, mir: MIR) -> MIR:
        self.mirs[mir.id] = mir
        return mir

    async def get_mir_all(self) -> list[MIR]:
        return [mir for mir in self.mirs.values() if not mir.borrado]

    async def get_by_id(self, mir_id: UUID) -> MIR | None:
        mir = self.mirs.get(mir_id)
        return mir if mir and not mir.borrado else None

    async def get_by_codigo_mir(self, codigo: str) -> MIR | None:
        return next(
            (
                mir
                for mir in self.mirs.values()
                if mir.codigo_mir == codigo and not mir.borrado
            ),
            None,
        )

    async def update_mir(self, mir: MIR) -> MIR:
        self.mirs[mir.id] = mir
        return mir


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, RepoFalso]]:
    repo = RepoFalso()
    app = FastAPI()
    app.include_router(modulo_router.router)
    app.dependency_overrides[modulo_router.get_uow] = UnidadFalsa
    monkeypatch.setattr(modulo_router, "MirRepositorySqlAlchemy", lambda uow: repo)
    with TestClient(app) as client:
        yield client, repo


def test_alta_consulta_edicion_y_baja_logica(api: tuple[TestClient, RepoFalso]) -> None:
    client, repo = api
    actor = uuid4()
    creado = client.post(
        "/mir",
        json={
            "codigo_mir": "26001",
            "descripcion": "Incidencia ficticia",
            "tipo": "Incidencia",
            "detectada_por_id": str(actor),
            "solucionado": False,
        },
    )
    assert creado.status_code == 201
    mir_id = creado.json()["id"]
    assert client.get("/mir").json()[0]["id"] == mir_id
    assert client.get("/mir/26001").json()["id"] == mir_id
    editado = client.patch(f"/mir/{mir_id}", json={"descripcion": "Cambio ficticio"})
    assert editado.status_code == 200
    assert editado.json()["descripcion"] == "Cambio ficticio"
    assert (
        client.delete(f"/mir/{mir_id}", params={"actor_id": str(actor)}).status_code
        == 204
    )
    assert client.get("/mir").json() == []
    assert client.get("/mir/26001").status_code == 404
    assert repo.mirs[UUID(mir_id)].borrado_por_id == actor


def test_los_errores_no_exponen_datos_y_una_baja_inexistente_da_404(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, _ = api
    assert (
        client.delete(f"/mir/{uuid4()}", params={"actor_id": str(uuid4())}).status_code
        == 404
    )
    assert (
        client.patch(f"/mir/{uuid4()}", json={"descripcion": "Ficticia"}).status_code
        == 404
    )


def test_una_mir_ya_solucionada_conserva_sus_datos(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, _ = api
    respuesta = client.post(
        "/mir",
        json={
            "codigo_mir": "26002",
            "descripcion": "Incidencia ficticia",
            "tipo": "Incidencia",
            "detectada_por_id": str(uuid4()),
            "solucionado": True,
            "solucion_adoptada": "Accion ficticia",
            "analisis_causas": "Causa ficticia",
            "algo_mas_que_hacer": "Seguimiento ficticio",
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["analisis_causas"] == "Causa ficticia"


def test_no_se_registra_una_mir_solucionada_sin_analisis(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    respuesta = client.post(
        "/mir",
        json={
            "codigo_mir": "26003",
            "descripcion": "Incidencia ficticia",
            "tipo": "Incidencia",
            "detectada_por_id": str(uuid4()),
            "solucionado": True,
        },
    )

    assert respuesta.status_code == 422
    assert repo.mirs == {}
