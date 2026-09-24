"""Alta, persistencia y listado por detector contra la BD desechable."""

import json
from datetime import datetime
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

HOY = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()


def crear(cliente: TestClient, detector: UUID, **cambios: object) -> dict[str, object]:
    datos: dict[str, object] = {
        "tipo": "Incidencia",
        "descripcion": "Incidencia ficticia.",
        "fecha_deteccion": HOY,
        "detectada_por_id": str(detector),
        "solucionado": False,
        "empresa_nombre": "Empresa Ficticia",
        "persona_contacto": "Persona Ficticia",
        "telefono": "0600123456",
        "correo_electronico": "contacto@ejemplo.test",
    }
    datos.update(cambios)
    respuesta = cliente.post("/mir", data={"datos": json.dumps(datos)})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_creacion_y_listado_solo_del_detector(
    cliente: TestClient, usuario_ficticio: UUID
) -> None:
    otro = uuid4()
    primero = crear(cliente, usuario_ficticio, codigo_cliente="CLIENTE-1")
    segundo = crear(cliente, usuario_ficticio)

    assert primero["codigo_mir"] != segundo["codigo_mir"]
    assert primero["estado"] == "EN_REVISION"
    assert primero["codigo_cliente"] == "CLIENTE-1"
    assert primero["telefono"] == "0600123456"
    assert primero["fecha_deteccion"] == HOY
    assert (
        cliente.get(f"/mir/{primero['codigo_mir']}").json()["empresa_nombre"]
        == "Empresa Ficticia"
    )
    listado = cliente.get("/mir", params={"detectada_por_id": str(usuario_ficticio)})
    assert listado.status_code == 200
    assert {mir["id"] for mir in listado.json()} == {primero["id"], segundo["id"]}
    assert cliente.get("/mir", params={"detectada_por_id": str(otro)}).json() == []


def test_archivos_se_vinculan_y_no_se_pierden(
    cliente: TestClient, usuario_ficticio: UUID
) -> None:
    datos = {
        "tipo": "Mejora",
        "descripcion": "Mejora ficticia.",
        "fecha_deteccion": HOY,
        "detectada_por_id": str(usuario_ficticio),
        "solucionado": False,
        "empresa_nombre": "Empresa Ficticia",
        "persona_contacto": "Persona Ficticia",
        "telefono": "0600123456",
        "correo_electronico": "contacto@ejemplo.test",
        "tipos_documento": ["pdf"],
    }
    respuesta = cliente.post(
        "/mir",
        data={"datos": json.dumps(datos)},
        files=[("archivos", ("evidencia.pdf", b"contenido", "application/pdf"))],
    )
    assert respuesta.status_code == 201, respuesta.text
    assert len(respuesta.json()["documento_ids"]) == 1


def test_tipo_de_archivo_faltante_no_crea_mir(
    cliente: TestClient, usuario_ficticio: UUID
) -> None:
    datos = {
        "tipo": "Mejora",
        "descripcion": "Mejora ficticia.",
        "fecha_deteccion": HOY,
        "detectada_por_id": str(usuario_ficticio),
        "solucionado": False,
        "empresa_nombre": "Empresa Ficticia",
        "persona_contacto": "Persona Ficticia",
        "telefono": "0600123456",
        "correo_electronico": "contacto@ejemplo.test",
    }
    respuesta = cliente.post(
        "/mir",
        data={"datos": json.dumps(datos)},
        files=[("archivos", ("evidencia.pdf", b"contenido", "application/pdf"))],
    )
    assert respuesta.status_code == 422
    assert (
        cliente.get("/mir", params={"detectada_por_id": str(usuario_ficticio)}).json()
        == []
    )
