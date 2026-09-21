from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from modules.usuarios.domain.Entities.usuario import Usuario
from modules.usuarios.domain.Enum.rol import Rol


class UsuarioRead(BaseModel):
    id: UUID
    correo: str
    nombre: str
    rol: Rol
    departamento: str
    activo: bool
    creado_en: datetime
    dado_de_baja_en: datetime | None

    @classmethod
    def from_dominio(cls, usuario: Usuario) -> UsuarioRead:
        return cls(
            id=usuario.id,
            correo=usuario.correo.valor,
            nombre=usuario.nombre,
            rol=usuario.rol,
            departamento=usuario.departamento.valor,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
            dado_de_baja_en=usuario.dado_de_baja_en,
        )


class RegistrarUsuarioDTO(BaseModel):
    correo: str
    rol: str
    departamento: str
    nombre: str
    activo: bool
    creado_en: datetime


class ActualizarUsuarioDTO(BaseModel):
    nombre: str | None = None
    rol: str | None = None
    departamento: str | None = None

    @model_validator(mode="after")
    def validar_al_menos_un_cambio(self) -> ActualizarUsuarioDTO:
        if self.nombre is None and self.rol is None and self.departamento is None:
            raise ValueError("debe proporcionarse nombre, rol o departamento")
        return self
