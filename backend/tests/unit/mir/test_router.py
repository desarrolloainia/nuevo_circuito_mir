import json
from collections.abc import Iterator
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.archivos.application.ports.file_storage import ArchivoSubido
from modules.archivos.domain.entities.documento import Documento
from modules.mir.api import router as modulo_router
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado


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

    async def reservar_numero(self, anio: int) -> int:
        return 1 + len(self.mirs)

    async def get_mir_all(self, detectada_por_id: UUID | None = None) -> list[MIR]:
        return [
            mir
            for mir in self.mirs.values()
            if not mir.borrado
            and (detectada_por_id is None or mir.detectada_por_id == detectada_por_id)
        ]

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

    async def filtrar_estado(self, estado: Estado) -> list[MIR]:
        return [
            mir
            for mir in self.mirs.values()
            if mir.estado == estado and not mir.borrado
        ]

    async def editar_estado(self, mir_id: UUID, estado: Estado) -> MIR:
        self.mirs[mir_id].estado = estado
        return self.mirs[mir_id]


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
    creado = client.post("/mir", data={"datos": json.dumps(datos(actor))})
    assert creado.status_code == 201
    mir_id = creado.json()["id"]
    assert (
        client.get("/mir", params={"detectada_por_id": str(actor)}).json()[0]["id"]
        == mir_id
    )
    assert client.get("/mir", params={"detectada_por_id": str(uuid4())}).json() == []
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


def datos(actor: UUID) -> dict[str, object]:
    return {
        "descripcion": "Incidencia ficticia",
        "tipo": "Incidencia",
        "fecha_deteccion": datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat(),
        "detectada_por_id": str(actor),
        "solucionado": False,
        "empresa_nombre": "Empresa Ficticia",
        "persona_contacto": "Persona Ficticia",
        "telefono": "0600123456",
        "correo_electronico": "contacto@ejemplo.test",
    }


def test_una_mir_ya_solucionada_conserva_sus_datos(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, _ = api
    payload = datos(uuid4()) | {
        "solucionado": True,
        "solucion_adoptada": "Accion ficticia",
        "analisis_causas": "Causa ficticia",
        "algo_mas_que_hacer": "Seguimiento ficticio",
    }
    respuesta = client.post("/mir", data={"datos": json.dumps(payload)})

    assert respuesta.status_code == 201
    assert respuesta.json()["analisis_causas"] == "Causa ficticia"


def test_no_se_registra_una_mir_solucionada_sin_analisis(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    respuesta = client.post(
        "/mir", data={"datos": json.dumps(datos(uuid4()) | {"solucionado": True})}
    )

    assert respuesta.status_code == 422
    assert repo.mirs == {}


def test_los_archivos_se_guardan_junto_a_la_mir(
    api: tuple[TestClient, RepoFalso], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, repo = api

    class StorageFalso:
        async def subir(
            self, nombre: str, contenido: bytes, content_type: str
        ) -> ArchivoSubido:
            assert contenido == b"evidencia"
            return ArchivoSubido(
                storage_id="ficticio", nombre=nombre, tamano_bytes=len(contenido)
            )

        async def eliminar(self, storage_id: str) -> None:
            return None

    class DocumentosFalsos:
        async def save(self, documento: Documento) -> Documento:
            return documento

    monkeypatch.setattr(modulo_router, "get_storage", StorageFalso)
    monkeypatch.setattr(
        modulo_router, "DocumentoRepositorySqlAlchemy", lambda uow: DocumentosFalsos()
    )
    payload = datos(uuid4()) | {"tipos_documento": ["pdf"]}
    respuesta = client.post(
        "/mir",
        data={"datos": json.dumps(payload)},
        files=[("archivos", ("evidencia.pdf", b"evidencia", "application/pdf"))],
    )

    assert respuesta.status_code == 201, respuesta.text
    mir = next(iter(repo.mirs.values()))
    assert respuesta.json()["documento_ids"] == [str(mir.documentos[0].id)]
    assert mir.documentos[0].nombre == "evidencia.pdf"
