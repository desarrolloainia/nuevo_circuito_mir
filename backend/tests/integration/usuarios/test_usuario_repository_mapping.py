from datetime import UTC, datetime

from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.Infrastructure.persistence.usuario_repository import (
    to_domain,
    to_orm,
)


def test_to_orm_y_to_domain_son_inversas():
    usuario = Usuario(
        correo=Correo("tecnico@ainia.test"),
        rol=Rol.TECNICO_CLD,
        departamento=Departamento("Calidad"),
    )

    usuario_orm = to_orm(usuario)
    usuario_reconstruido = to_domain(usuario_orm)

    assert usuario_reconstruido == usuario


def test_to_orm_serializa_rol_y_departamento_como_texto_plano():
    usuario = Usuario(
        correo=Correo("tecnico@ainia.test"),
        rol=Rol.TECNICO_CLD,
        departamento=Departamento("Calidad"),
        activo=False,
        dado_de_baja_en=datetime.now(UTC),
    )

    usuario_orm = to_orm(usuario)

    assert usuario_orm.correo == "tecnico@ainia.test"
    assert usuario_orm.rol == "TECNICO_CLD"
    assert usuario_orm.departamento == "Calidad"
    assert usuario_orm.activo is False
    assert usuario_orm.dado_de_baja_en is not None
