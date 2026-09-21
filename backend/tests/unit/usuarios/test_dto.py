from datetime import UTC, datetime

from modules.usuarios.api.dto import ActualizarUsuarioDTO, UsuarioRead
from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol


def test_usuario_read_incluye_el_nombre():
    usuario = Usuario(
        correo=Correo("tecnico@ainia.test"),
        nombre="Ana Técnico",
        rol=Rol.TECNICO_CLD,
        departamento=Departamento("Calidad"),
        creado_en=datetime.now(UTC),
    )

    lectura = UsuarioRead.from_dominio(usuario)

    assert lectura.nombre == "Ana Técnico"


def test_actualizar_usuario_dto_acepta_solo_nombre():
    dto = ActualizarUsuarioDTO(nombre="Ana Gómez")

    assert dto.nombre == "Ana Gómez"
