"""Invariantes del agregado MIR en el registro inicial."""

from datetime import date
from typing import Any
from uuid import uuid4

import pytest

from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir
from modules.mir.domain.exceptions.exceptions import ErrorValidacionMir
from tests.unit.mir.dobles import instante

REGISTRO = instante(2026, 9, 21)


def crear(**cambios: Any) -> MIR:
    datos: dict[str, Any] = {
        "codigo_mir": "26001",
        "descripcion": "Se detecto una desviacion en el proceso.",
        "tipo": TipoMir.INCIDENCIA,
        "fecha_deteccion": date(2026, 9, 20),
        "detectada_por_id": uuid4(),
        "solucionado": False,
        "creado_en": REGISTRO,
    }
    datos.update(cambios)
    return MIR(**datos)


def campos_invalidos(**cambios: Any) -> list[str]:
    with pytest.raises(ErrorValidacionMir) as error:
        crear(**cambios)
    return [campo.campo for campo in error.value.errores]


def test_una_mir_valida_queda_en_revision_con_sus_datos():
    mir = crear()

    assert mir.estado is Estado.EN_REVISION
    assert mir.codigo_mir == "26001"
    assert mir.modificado_en == mir.creado_en


def test_una_descripcion_solo_con_espacios_se_considera_ausente():
    assert campos_invalidos(descripcion="   ") == ["descripcion"]
    assert campos_invalidos(descripcion="") == ["descripcion"]


def test_el_tipo_debe_pertenecer_al_catalogo_inicial():
    assert campos_invalidos(tipo="Sugerencia") == ["tipo"]
    for tipo in (TipoMir.MEJORA, TipoMir.INCIDENCIA):
        assert crear(tipo=tipo).tipo is tipo


def test_no_puede_crearse_una_mir_en_un_estado_distinto_de_en_revision():
    assert campos_invalidos(estado=Estado.EN_PROGRESO) == ["estado"]


def test_la_fecha_de_deteccion_no_puede_ser_posterior_al_dia_de_registro():
    assert crear(fecha_deteccion=date(2026, 9, 21)).fecha_deteccion == date(2026, 9, 21)
    assert crear(fecha_deteccion=date(2020, 1, 1)).fecha_deteccion == date(2020, 1, 1)
    assert campos_invalidos(fecha_deteccion=date(2026, 9, 22)) == ["fecha_deteccion"]


def test_el_dia_de_registro_se_calcula_en_la_zona_horaria_de_negocio():
    # 21/09/2026 23:30 UTC ya es 22/09/2026 en Europe/Madrid.
    mir = crear(creado_en=instante(2026, 9, 21, 23), fecha_deteccion=date(2026, 9, 22))

    assert mir.fecha_deteccion == date(2026, 9, 22)


def test_los_datos_de_solucion_no_se_conservan_si_la_mir_no_llego_solucionada():
    mir = crear(
        solucionado=False,
        solucion_adoptada="Se cambio el envase",
        analisis_causas="Manipulacion incorrecta",
        algo_mas_que_hacer="Nada",
    )

    assert mir.solucion_adoptada is None
    assert mir.analisis_causas is None
    assert mir.algo_mas_que_hacer is None


def test_los_datos_de_reclamante_no_se_conservan_para_mejora_o_incidencia():
    mir = crear(
        tipo=TipoMir.MEJORA,
        nombre_reclamante="Persona Ficticia",
        empresa_reclamante="Empresa Ficticia",
    )

    assert mir.nombre_reclamante is None
    assert mir.empresa_reclamante is None


def test_se_acumulan_todos_los_campos_invalidos_en_un_unico_error():
    assert set(
        campos_invalidos(
            descripcion=" ", tipo="Sugerencia", fecha_deteccion=date(2026, 9, 30)
        )
    ) == {
        "descripcion",
        "tipo",
        "fecha_deteccion",
    }


def test_una_mir_solucionada_exige_los_tres_datos_de_solucion():
    solucionada: dict[str, Any] = {
        "solucionado": True,
        "solucion_adoptada": "Se sustituyo el envase afectado.",
        "analisis_causas": "El precinto se dano durante la manipulacion.",
        "algo_mas_que_hacer": "Revisar el metodo de manipulacion.",
    }
    mir = crear(**solucionada)

    assert mir.solucion_adoptada == "Se sustituyo el envase afectado."
    assert mir.analisis_causas == "El precinto se dano durante la manipulacion."
    assert mir.algo_mas_que_hacer == "Revisar el metodo de manipulacion."

    for campo in ("solucion_adoptada", "analisis_causas", "algo_mas_que_hacer"):
        assert campos_invalidos(**{**solucionada, campo: None}) == [campo]
        assert campos_invalidos(**{**solucionada, campo: "   "}) == [campo]


def test_una_mir_solucionada_sin_ningun_dato_acumula_los_tres_campos():
    assert campos_invalidos(solucionado=True) == [
        "solucion_adoptada",
        "analisis_causas",
        "algo_mas_que_hacer",
    ]


def test_una_reclamacion_exige_persona_y_empresa_reclamante():
    reclamacion: dict[str, Any] = {
        "tipo": TipoMir.RECLAMACION,
        "nombre_reclamante": "Persona Ficticia",
        "empresa_reclamante": "Empresa Ficticia",
    }
    mir = crear(**reclamacion)

    assert mir.nombre_reclamante == "Persona Ficticia"
    assert mir.empresa_reclamante == "Empresa Ficticia"

    for campo in ("nombre_reclamante", "empresa_reclamante"):
        assert campos_invalidos(**{**reclamacion, campo: None}) == [campo]
        assert campos_invalidos(**{**reclamacion, campo: " "}) == [campo]
