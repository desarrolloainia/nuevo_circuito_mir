import asyncio
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.jefe_calidad.api import router as modulo_router
from modules.mir.domain.Enum.estado import Estado
from modules.usuarios.domain.Enum.rol import Rol
from tests.unit.jefe_calidad.test_asignar_responsable import usuario_ficticio
from tests.unit.jefe_calidad.test_denegar_mir import mir_ficticia
from tests.unit.mir.test_router import RepoFalso, UnidadFalsa
from tests.unit.usuarios.dobles import UsuarioRepositoryEnMemoria

USUARIOS = UsuarioRepositoryEnMemoria()


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, RepoFalso]]:
    repo = RepoFalso()
    app = FastAPI()
    app.include_router(modulo_router.router)
    app.dependency_overrides[modulo_router.get_uow] = UnidadFalsa
    monkeypatch.setattr(modulo_router, "MirRepositorySqlAlchemy", lambda uow: repo)
    monkeypatch.setattr(
        modulo_router, "UsuarioRepositorySqlAlchemy", lambda uow: USUARIOS
    )
    with TestClient(app) as client:
        yield client, repo


def test_el_jefe_de_cld_solo_recupera_las_mir_en_revision(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    en_revision = mir_ficticia()
    rechazada = mir_ficticia(estado=Estado.RECHAZADA)
    repo.mirs = {en_revision.id: en_revision, rechazada.id: rechazada}

    respuesta = client.get("/jefe-calidad/mir")

    assert respuesta.status_code == 200
    assert [mir["id"] for mir in respuesta.json()] == [str(en_revision.id)]


def test_denegar_por_http_deja_la_mir_rechazada(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia(tecnico_cld_id=None)
    repo.mirs[mir.id] = mir
    jefe = usuario_ficticio(Rol.JEFE_CLD)
    asyncio.run(USUARIOS.guardar(jefe))

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/denegar", json={"actor_id": str(jefe.id)}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == Estado.RECHAZADA


def test_denegar_por_http_sin_ser_jefe_da_403(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia()
    repo.mirs[mir.id] = mir
    tecnico = usuario_ficticio(Rol.TECNICO_CLD)
    mir.tecnico_cld_id = tecnico.id
    asyncio.run(USUARIOS.guardar(tecnico))

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/denegar", json={"actor_id": str(tecnico.id)}
    )

    assert respuesta.status_code == 403
    assert mir.estado == Estado.EN_REVISION


def test_denegar_por_http_con_actor_inexistente_da_403(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia()
    repo.mirs[mir.id] = mir

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/denegar", json={"actor_id": str(uuid4())}
    )

    assert respuesta.status_code == 403
    assert mir.estado == Estado.EN_REVISION


def test_denegar_por_http_una_mir_inexistente_da_404(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, _ = api

    respuesta = client.post(
        f"/jefe-calidad/mir/{uuid4()}/denegar", json={"actor_id": str(uuid4())}
    )

    assert respuesta.status_code == 404


def test_asignar_por_http_un_tecnico_de_cld_lo_deja_en_la_mir(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia(tecnico_cld_id=None)
    repo.mirs[mir.id] = mir
    tecnico = usuario_ficticio(Rol.TECNICO_CLD)
    asyncio.run(USUARIOS.guardar(tecnico))

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/asignar-tecnico",
        json={"tecnico_cld_id": str(tecnico.id)},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["tecnico_cld_id"] == str(tecnico.id)
    assert respuesta.json()["estado"] == Estado.EN_PROGRESO


def test_asignar_por_http_un_usuario_sin_rol_de_tecnico_da_422(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia(tecnico_cld_id=None)
    repo.mirs[mir.id] = mir
    ejecutor = usuario_ficticio(Rol.EJECUTOR)
    asyncio.run(USUARIOS.guardar(ejecutor))

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/asignar-tecnico",
        json={"tecnico_cld_id": str(ejecutor.id)},
    )

    assert respuesta.status_code == 422
    assert mir.tecnico_cld_id is None


def test_asignar_por_http_un_usuario_inexistente_da_404(
    api: tuple[TestClient, RepoFalso],
) -> None:
    client, repo = api
    mir = mir_ficticia(tecnico_cld_id=None)
    repo.mirs[mir.id] = mir

    respuesta = client.post(
        f"/jefe-calidad/mir/{mir.id}/asignar-tecnico",
        json={"tecnico_cld_id": str(uuid4())},
    )

    assert respuesta.status_code == 404
