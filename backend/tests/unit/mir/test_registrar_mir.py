"""Orquestacion del alta de MIR: validacion, codigo anual y transaccion unica."""

import asyncio
from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from modules.mir.application.uses_cases.registrar_mir import registrar_mir

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import (
    DocumentosYaVinculadosError,
    ErrorValidacionMir,
)
from tests.unit.mir.dobles import (
    ConsultaDetectoresFalsa,
    MirRepositorioFalso,
    RelojFijo,
    UnidadTrabajoFalsa,
    VinculoDocumentosFalso,
    instante,
)


class Escenario:
    def __init__(self, registro: Any = None, **repositorio: Any) -> None:
        self.detector_id = uuid4()
        self.detectores = ConsultaDetectoresFalsa([self.detector_id])
        self.documentos = VinculoDocumentosFalso()
        self.repositorio = MirRepositorioFalso(**repositorio)
        self.uow = UnidadTrabajoFalsa()
        self.reloj = RelojFijo(registro or instante(2026, 9, 21))

    async def registrar(self, **cambios: Any) -> MIR:
        datos: dict[str, Any] = {
            "tipo": TipoMir.INCIDENCIA,
            "descripcion": "Se detecto una desviacion en el proceso.",
            "fecha_deteccion": date(2026, 9, 20),
            "detectada_por_id": self.detector_id,
            "solucionado": False,
        }
        datos.update(cambios)
        return await registrar_mir(
            **datos,
            detectores=self.detectores,
            documentos=self.documentos,
            repositorio=self.repositorio,
            uow=self.uow,
            ahora=self.reloj,
        )


def test_un_alta_valida_se_guarda_y_confirma_una_sola_vez():
    async def caso() -> None:
        escenario = Escenario()

        mir = await escenario.registrar()

        assert mir.codigo_mir == "26001"
        assert mir.estado is Estado.EN_REVISION
        assert escenario.repositorio.guardadas == [mir]
        assert escenario.uow.commits == 1
        assert escenario.uow.rollbacks == 0

    asyncio.run(caso())


def test_un_detector_inexistente_rechaza_el_alta_sin_reservar_codigo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(detectada_por_id=uuid4())

        assert [campo.campo for campo in error.value.errores] == ["detectada_por_id"]
        assert escenario.repositorio.reservas == []
        assert escenario.uow.commits == 0

    asyncio.run(caso())


def test_los_errores_de_datos_y_de_detector_se_devuelven_juntos():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(descripcion="   ", detectada_por_id=uuid4())

        assert {campo.campo for campo in error.value.errores} == {
            "descripcion",
            "detectada_por_id",
        }
        assert escenario.repositorio.guardadas == []

    asyncio.run(caso())


def test_el_anio_del_codigo_es_el_del_dia_de_registro_en_europa_madrid():
    async def caso() -> None:
        # 31/12/2026 23:30 UTC ya es 01/01/2027 en Europe/Madrid.
        escenario = Escenario(registro=instante(2026, 12, 31, 23))

        mir = await escenario.registrar(fecha_deteccion=date(2026, 12, 31))

        assert mir.codigo_mir == "27001"
        assert escenario.repositorio.reservas == [2027]

    asyncio.run(caso())


def test_la_secuencia_usa_tres_posiciones_como_minimo_y_crece_sin_perder_el_anio():
    async def caso() -> None:
        escenario = Escenario()
        escenario.repositorio.contadores[2026] = 999

        mir = await escenario.registrar()

        assert mir.codigo_mir == "261000"

    asyncio.run(caso())


def test_un_fallo_al_guardar_revierte_la_transaccion_sin_confirmar_codigo():
    async def caso() -> None:
        escenario = Escenario(fallar_al_guardar=True)

        with pytest.raises(RuntimeError):
            _ = await escenario.registrar()

        assert escenario.uow.commits == 0
        assert escenario.uow.rollbacks == 1

    asyncio.run(caso())


def test_una_mir_solucionada_conserva_sus_tres_datos_de_solucion():
    async def caso() -> None:
        escenario = Escenario()

        mir = await escenario.registrar(
            solucionado=True,
            solucion_adoptada="Se sustituyo el envase afectado.",
            analisis_causas="El precinto se dano durante la manipulacion.",
            algo_mas_que_hacer="Revisar el metodo de manipulacion.",
        )

        assert mir.solucionado is True
        assert mir.algo_mas_que_hacer == "Revisar el metodo de manipulacion."
        assert escenario.uow.commits == 1

    asyncio.run(caso())


def test_una_mir_solucionada_incompleta_no_reserva_codigo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(solucionado=True, solucion_adoptada="  ")

        assert {campo.campo for campo in error.value.errores} == {
            "solucion_adoptada",
            "analisis_causas",
            "algo_mas_que_hacer",
        }
        assert escenario.repositorio.reservas == []

    asyncio.run(caso())


def test_una_reclamacion_valida_conserva_reclamante_y_empresa():
    async def caso() -> None:
        escenario = Escenario()

        mir = await escenario.registrar(
            tipo=TipoMir.RECLAMACION,
            nombre_reclamante="Persona Ficticia",
            empresa_reclamante="Empresa Ficticia",
        )

        assert mir.nombre_reclamante == "Persona Ficticia"
        assert mir.empresa_reclamante == "Empresa Ficticia"

    asyncio.run(caso())


def test_una_reclamacion_sin_empresa_se_rechaza_sin_reservar_codigo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(
                tipo=TipoMir.RECLAMACION, nombre_reclamante="Persona Ficticia"
            )

        assert [campo.campo for campo in error.value.errores] == ["empresa_reclamante"]
        assert escenario.repositorio.reservas == []

    asyncio.run(caso())


def test_una_mejora_no_exige_ni_conserva_datos_de_reclamante():
    async def caso() -> None:
        escenario = Escenario()

        mir = await escenario.registrar(
            tipo=TipoMir.MEJORA, nombre_reclamante="Persona Ficticia"
        )

        assert mir.nombre_reclamante is None
        assert mir.empresa_reclamante is None

    asyncio.run(caso())


def documentos_disponibles(escenario: Escenario, cuantos: int) -> list[Any]:
    ids = [uuid4() for _ in range(cuantos)]
    escenario.documentos.documentos.update({documento_id: None for documento_id in ids})
    return ids


def test_una_mir_sin_adjuntos_no_consulta_el_modulo_documental():
    async def caso() -> None:
        escenario = Escenario()

        _ = await escenario.registrar(documento_ids=[])

        assert escenario.documentos.bloqueados == []
        assert escenario.documentos.vinculados == []

    asyncio.run(caso())


def test_hasta_diez_adjuntos_disponibles_se_vinculan_a_la_mir_creada():
    async def caso() -> None:
        escenario = Escenario()
        ids = documentos_disponibles(escenario, 10)

        mir = await escenario.registrar(documento_ids=ids)

        assert escenario.documentos.vinculados == [(ids, mir.id)]
        assert escenario.uow.commits == 1

    asyncio.run(caso())


def test_mas_de_diez_adjuntos_se_rechazan():
    async def caso() -> None:
        escenario = Escenario()
        ids = documentos_disponibles(escenario, 11)

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(documento_ids=ids)

        assert [campo.campo for campo in error.value.errores] == ["documento_ids"]
        assert escenario.repositorio.reservas == []

    asyncio.run(caso())


def test_una_referencia_repetida_se_rechaza():
    async def caso() -> None:
        escenario = Escenario()
        (documento_id,) = documentos_disponibles(escenario, 1)

        with pytest.raises(ErrorValidacionMir):
            _ = await escenario.registrar(documento_ids=[documento_id, documento_id])

        assert escenario.documentos.vinculados == []

    asyncio.run(caso())


def test_una_referencia_inexistente_se_rechaza_sin_vincular_las_demas():
    async def caso() -> None:
        escenario = Escenario()
        ids = documentos_disponibles(escenario, 1)

        with pytest.raises(ErrorValidacionMir) as error:
            _ = await escenario.registrar(documento_ids=[*ids, uuid4()])

        assert [campo.campo for campo in error.value.errores] == ["documento_ids"]
        assert escenario.documentos.vinculados == []
        assert escenario.uow.commits == 0

    asyncio.run(caso())


def test_una_referencia_ya_vinculada_a_otra_mir_se_rechaza():
    async def caso() -> None:
        escenario = Escenario()
        (documento_id,) = documentos_disponibles(escenario, 1)
        escenario.documentos.documentos[documento_id] = uuid4()

        with pytest.raises(DocumentosYaVinculadosError):
            _ = await escenario.registrar(documento_ids=[documento_id])

        assert escenario.uow.commits == 0
        assert escenario.uow.rollbacks == 1

    asyncio.run(caso())


def test_los_documentos_se_reutilizan_tras_un_alta_fallida():
    async def caso() -> None:
        escenario = Escenario(fallar_al_guardar=True)
        ids = documentos_disponibles(escenario, 2)

        with pytest.raises(RuntimeError):
            _ = await escenario.registrar(documento_ids=ids)

        assert escenario.documentos.vinculados == []
        assert all(escenario.documentos.documentos[i] is None for i in ids)

        escenario.repositorio.fallar_al_guardar = False
        mir = await escenario.registrar(documento_ids=ids)

        assert escenario.documentos.vinculados == [(ids, mir.id)]

    asyncio.run(caso())
