import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import (
    DatoObligatorioFaltanteError,
    FormatoCorreoInvalidoError,
    UsuarioInactivoError,
)

_FORMATO_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Correo:
    valor: str

    def __post_init__(self) -> None:
        if not _FORMATO_CORREO.match(self.valor):
            raise FormatoCorreoInvalidoError(self.valor)


@dataclass(frozen=True)
class Departamento:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor.strip():
            raise DatoObligatorioFaltanteError("departamento")


@dataclass
class Usuario:
    correo: Correo
    nombre: str
    rol: Rol
    departamento: Departamento
    id: UUID = field(default_factory=uuid4)
    activo: bool = True
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    dado_de_baja_en: datetime | None = None

    def dar_de_baja(self) -> None:
        if not self.activo:
            return
        self.activo = False
        self.dado_de_baja_en = datetime.now(UTC)

    def actualizar(
        self,
        rol: Rol | None = None,
        departamento: Departamento | None = None,
        nombre: str | None = None,
    ) -> None:
        if not self.activo:
            raise UsuarioInactivoError(self.correo.valor)
        if rol is not None:
            self.rol = rol
        if departamento is not None:
            self.departamento = departamento
        if nombre is not None:
            self.nombre = nombre
