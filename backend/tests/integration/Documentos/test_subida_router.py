"""Contrato HTTP de POST /archivos."""

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from modules.archivos.domain.entities.documento import TAMANO_MAXIMO_BYTES
from tests.integration.conftest import StorageEnMemoria

CAMPOS_RESPUESTA = {"id", "nombre", "tipo", "tamano_bytes", "creado_por", "creado_en"}


def subir(cliente: TestClient, creador: UUID, contenido: bytes = b"evidencia"):
    return cliente.post(
        "/archivos",
        files={"archivo": ("evidencia-ficticia.pdf", contenido, "application/pdf")},
        data={"tipo": "pdf", "creado_por": str(creador)},
    )


def test_una_carga_valida_responde_201_sin_exponer_el_identificador_remoto(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = subir(cliente, usuario_ficticio)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert set(cuerpo) == CAMPOS_RESPUESTA
    assert cuerpo["nombre"] == "evidencia-ficticia.pdf"
    assert cuerpo["tamano_bytes"] == len(b"evidencia")


def test_un_archivo_vacio_responde_422(cliente: TestClient, usuario_ficticio: UUID):
    assert subir(cliente, usuario_ficticio, contenido=b"").status_code == 422


def test_un_creador_inexistente_responde_422(cliente: TestClient):
    assert subir(cliente, uuid4()).status_code == 422


def test_un_archivo_mayor_del_limite_responde_413(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = subir(
        cliente, usuario_ficticio, contenido=b"x" * (TAMANO_MAXIMO_BYTES + 1)
    )

    assert respuesta.status_code == 413


def test_un_fallo_del_almacenamiento_responde_502(
    cliente: TestClient, usuario_ficticio: UUID, storage: StorageEnMemoria
):
    storage.fallar = True

    respuesta = subir(cliente, usuario_ficticio)

    assert respuesta.status_code == 502
    assert "evidencia-ficticia.pdf" not in respuesta.text


def test_los_errores_de_carga_no_devuelven_el_nombre_del_archivo(
    cliente: TestClient, usuario_ficticio: UUID
):
    vacio = subir(cliente, usuario_ficticio, contenido=b"")
    grande = subir(
        cliente, usuario_ficticio, contenido=b"x" * (TAMANO_MAXIMO_BYTES + 1)
    )

    for respuesta in (vacio, grande):
        assert "evidencia-ficticia.pdf" not in respuesta.text
        assert "remoto-" not in respuesta.text
