from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modules.mir.api.dto import ActualizarMirDTO, CrearMirDTO, MirDTO
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.domain.Enum.tipo import TipoMir


def test_crear_mir_acepta_los_datos_que_recibe_el_caso_de_uso() -> None:
    datos = CrearMirDTO(
        descripcion="Desviacion detectada.",
        tipo=TipoMir.INCIDENCIA,
        fecha_deteccion=date(2026, 9, 20),
        detectada_por_id=uuid4(),
        solucionado=False,
        empresa_nombre="Empresa Ficticia",
        persona_contacto="Persona Ficticia",
        telefono="0600123456",
        correo_electronico="contacto@ejemplo.test",
    )

    assert datos.tipo is TipoMir.INCIDENCIA
    assert datos.prioridad is None


def test_crear_mir_rechaza_un_tipo_ajeno_al_dominio() -> None:
    with pytest.raises(ValidationError):
        _ = CrearMirDTO.model_validate(
            {
                "codigo_mir": "26001",
                "descripcion": "Desviacion detectada.",
                "tipo": "desconocido",
                "detectada_por_id": str(uuid4()),
                "solucionado": False,
            }
        )


def test_actualizar_mir_acepta_cambios_parciales() -> None:
    datos = ActualizarMirDTO(descripcion="Nueva descripcion.")

    assert datos.model_dump(exclude_unset=True) == {"descripcion": "Nueva descripcion."}


def test_mir_dto_refleja_la_entidad_sin_datos_de_almacenamiento() -> None:
    mir = MIR(
        id=uuid4(),
        codigo_mir="26001",
        descripcion="Desviacion detectada.",
        tipo=TipoMir.INCIDENCIA,
        estado=Estado.EN_REVISION,
        detectada_por_id=uuid4(),
        solucionado=False,
    )

    datos = MirDTO.from_dominio(mir)

    assert datos.id == mir.id
    assert datos.estado is Estado.EN_REVISION
    assert datos.documento_ids == []
    assert "storage_id" not in datos.model_dump()
