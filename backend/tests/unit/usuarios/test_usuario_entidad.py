from datetime import UTC, datetime

import pytest

from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import (
    DatoObligatorioFaltanteError,
    FormatoCorreoInvalidoError,
)


def test_correo_con_formato_invalido_lanza_error():
    with pytest.raises(FormatoCorreoInvalidoError):
        Correo("correo-sin-arroba")


def test_correo_con_formato_valido_no_lanza_error():
    correo = Correo("tecnico@ainia.test")

    assert correo.valor == "tecnico@ainia.test"


def test_departamento_vacio_lanza_error():
    with pytest.raises(DatoObligatorioFaltanteError):
        Departamento("   ")


def test_departamento_valido_no_lanza_error():
    departamento = Departamento("Calidad")

    assert departamento.valor == "Calidad"


def test_usuario_no_se_construye_sin_correo_valido():
    with pytest.raises(FormatoCorreoInvalidoError):
        Usuario(
            correo=Correo("correo-invalido"),
            nombre="Ana Técnico",
            rol=Rol.TECNICO_CLD,
            departamento=Departamento("Calidad"),
        )


def test_usuario_no_se_construye_sin_departamento():
    with pytest.raises(DatoObligatorioFaltanteError):
        Usuario(
            correo=Correo("tecnico@ainia.test"),
            nombre="Ana Técnico",
            rol=Rol.TECNICO_CLD,
            departamento=Departamento(""),
        )


def test_dar_de_baja_fija_inactivo_y_fecha_de_baja():
    usuario = Usuario(
        correo=Correo("tecnico@ainia.test"),
        nombre="Ana Técnico",
        rol=Rol.TECNICO_CLD,
        departamento=Departamento("Calidad"),
    )

    usuario.dar_de_baja()

    assert usuario.activo is False
    assert usuario.dado_de_baja_en is not None
    assert usuario.dado_de_baja_en <= datetime.now(UTC)


def test_dar_de_baja_dos_veces_es_idempotente():
    usuario = Usuario(
        correo=Correo("tecnico@ainia.test"),
        nombre="Ana Técnico",
        rol=Rol.TECNICO_CLD,
        departamento=Departamento("Calidad"),
    )

    usuario.dar_de_baja()
    primera_fecha_de_baja = usuario.dado_de_baja_en
    usuario.dar_de_baja()

    assert usuario.activo is False
    assert usuario.dado_de_baja_en == primera_fecha_de_baja
