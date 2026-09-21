from importlib import import_module
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_aplicacion_monta_los_endpoints_de_usuarios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://usuario:contrasena@localhost/circuito_mir_test",
    )
    app = cast(FastAPI, import_module("main").app)
    with TestClient(app) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert client.get("/docs").status_code == 200
    rutas = {
        (ruta, metodo.upper())
        for ruta, operaciones in response.json()["paths"].items()
        for metodo in operaciones
    }

    assert ("/usuarios", "POST") in rutas
    assert ("/usuarios", "GET") in rutas
    assert ("/usuarios/{correo}", "GET") in rutas
    assert ("/usuarios/{correo}", "PATCH") in rutas
    assert ("/usuarios/{correo}", "DELETE") in rutas
    assert ("/archivos/", "GET") in rutas
    assert ("/archivos/{documento_id}", "DELETE") in rutas
    assert ("/archivos/{documento_id}/contenido", "GET") in rutas
