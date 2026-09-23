"""Contrato HTTP de POST /mir."""

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

HOY = datetime.now(ZoneInfo("Europe/Madrid")).date()
CODIGO_ESPERADO = f"{HOY.year % 100:02d}001"

CAMPOS_RESPUESTA = {
    "id",
    "codigo_mir",
    "tipo",
    "descripcion",
    "estado",
    "fecha_deteccion",
    "detectada_por_id",
    "solucionado",
    "solucion_adoptada",
    "analisis_causas",
    "algo_mas_que_hacer",
    "nombre_reclamante",
    "empresa_reclamante",
    "documento_ids",
    "creado_en",
    "modificado_en",
}


def peticion(detector_id: UUID, **cambios: Any) -> dict[str, Any]:
    datos: dict[str, Any] = {
        "tipo": "Incidencia",
        "descripcion": "Se detecto una desviacion en el proceso.",
        "fecha_deteccion": HOY.isoformat(),
        "detectada_por_id": str(detector_id),
        "solucionado": False,
    }
    datos.update(cambios)
    return datos


def test_un_alta_valida_responde_201_con_la_mir_registrada(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post("/mir", json=peticion(usuario_ficticio))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert set(cuerpo) == CAMPOS_RESPUESTA
    assert cuerpo["codigo_mir"] == CODIGO_ESPERADO
    assert cuerpo["estado"] == "EN_REVISION"
    assert cuerpo["documento_ids"] == []
    assert cuerpo["solucion_adoptada"] is None
    assert cuerpo["nombre_reclamante"] is None
    assert date.fromisoformat(cuerpo["fecha_deteccion"]) == HOY


def test_los_datos_invalidos_responden_422_con_la_lista_de_campos(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post(
        "/mir",
        json=peticion(
            usuario_ficticio,
            descripcion="   ",
            fecha_deteccion=date(HOY.year + 1, 1, 1).isoformat(),
        ),
    )

    assert respuesta.status_code == 422
    detalle = respuesta.json()["detail"]
    assert {error["field"] for error in detalle} == {"descripcion", "fecha_deteccion"}
    assert all(set(error) == {"field", "message"} for error in detalle)


def test_un_detector_inexistente_responde_422_sin_consumir_codigo(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post("/mir", json=peticion(uuid4()))

    assert respuesta.status_code == 422
    assert [error["field"] for error in respuesta.json()["detail"]] == [
        "detectada_por_id"
    ]

    siguiente = cliente.post("/mir", json=peticion(usuario_ficticio))
    assert siguiente.json()["codigo_mir"] == CODIGO_ESPERADO


def test_una_mir_solucionada_devuelve_sus_tres_datos_de_solucion(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post(
        "/mir",
        json=peticion(
            usuario_ficticio,
            solucionado=True,
            solucion_adoptada="Se sustituyo el envase afectado.",
            analisis_causas="El precinto se dano durante la manipulacion.",
            algo_mas_que_hacer="Revisar el metodo de manipulacion.",
        ),
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["solucionado"] is True
    assert cuerpo["analisis_causas"] == "El precinto se dano durante la manipulacion."


def test_una_mir_solucionada_sin_datos_responde_422_con_los_tres_campos(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post("/mir", json=peticion(usuario_ficticio, solucionado=True))

    assert respuesta.status_code == 422
    assert {error["field"] for error in respuesta.json()["detail"]} == {
        "solucion_adoptada",
        "analisis_causas",
        "algo_mas_que_hacer",
    }


def test_una_reclamacion_sin_reclamante_responde_422(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post(
        "/mir", json=peticion(usuario_ficticio, tipo="Reclamación")
    )

    assert respuesta.status_code == 422
    assert {error["field"] for error in respuesta.json()["detail"]} == {
        "nombre_reclamante",
        "empresa_reclamante",
    }


def test_una_reclamacion_completa_responde_201_con_el_reclamante(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post(
        "/mir",
        json=peticion(
            usuario_ficticio,
            tipo="Reclamación",
            nombre_reclamante="Persona Ficticia",
            empresa_reclamante="Empresa Ficticia",
        ),
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "Reclamación"
    assert cuerpo["empresa_reclamante"] == "Empresa Ficticia"


def subir_documento_de_prueba(cliente: TestClient, creador: UUID) -> str:
    respuesta = cliente.post(
        "/archivos",
        files={"archivo": ("evidencia-ficticia.pdf", b"evidencia", "application/pdf")},
        data={"tipo": "pdf", "creado_por": str(creador)},
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def test_una_mir_con_adjuntos_los_vincula_una_sola_vez(
    cliente: TestClient, usuario_ficticio: UUID
):
    documento_id = subir_documento_de_prueba(cliente, usuario_ficticio)

    respuesta = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=[documento_id])
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["documento_ids"] == [documento_id]

    reutilizacion = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=[documento_id])
    )
    assert reutilizacion.status_code == 409


def test_una_referencia_inexistente_responde_422_sin_vincular_nada(
    cliente: TestClient, usuario_ficticio: UUID
):
    documento_id = subir_documento_de_prueba(cliente, usuario_ficticio)

    respuesta = cliente.post(
        "/mir",
        json=peticion(usuario_ficticio, documento_ids=[documento_id, str(uuid4())]),
    )

    assert respuesta.status_code == 422
    assert [error["field"] for error in respuesta.json()["detail"]] == ["documento_ids"]

    # El documento sigue disponible para un reintento.
    reintento = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=[documento_id])
    )
    assert reintento.status_code == 201


def test_once_adjuntos_responden_422(cliente: TestClient, usuario_ficticio: UUID):
    documentos = [str(uuid4()) for _ in range(11)]

    respuesta = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=documentos)
    )

    assert respuesta.status_code == 422


def test_los_errores_no_devuelven_datos_personales_ni_contenido_de_la_mir(
    cliente: TestClient, usuario_ficticio: UUID
):
    respuesta = cliente.post(
        "/mir",
        json=peticion(
            usuario_ficticio,
            tipo="Reclamación",
            descripcion="   ",
            nombre_reclamante="Persona Ficticia",
            empresa_reclamante="Empresa Ficticia",
            fecha_deteccion=date(HOY.year + 1, 1, 1).isoformat(),
        ),
    )

    assert respuesta.status_code == 422
    for valor in ("Persona Ficticia", "Empresa Ficticia", str(usuario_ficticio)):
        assert valor not in respuesta.text


def test_el_conflicto_de_adjuntos_no_devuelve_identificadores_remotos(
    cliente: TestClient, usuario_ficticio: UUID
):
    documento_id = subir_documento_de_prueba(cliente, usuario_ficticio)
    _ = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=[documento_id])
    )

    respuesta = cliente.post(
        "/mir", json=peticion(usuario_ficticio, documento_ids=[documento_id])
    )

    assert respuesta.status_code == 409
    assert "remoto-" not in respuesta.text
    assert documento_id not in respuesta.text
