from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.archivos.domain.Enum.estado_documetno import TipoDocumento


class DocumentoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    tipo: TipoDocumento
    storage_id: str
    creado_por: UUID
    creado_en: datetime


class EditarDocumentoDTO(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    contenido: bytes | None = None
    content_type: str | None = Field(default=None, min_length=1)
    tipo: TipoDocumento | None = None

    @model_validator(mode="after")
    def validar_cambios(self):
        if all(
            value is None
            for value in (self.nombre, self.contenido, self.content_type, self.tipo)
        ):
            raise ValueError("debe proporcionarse al menos un cambio")
        if self.contenido is not None and (
            self.nombre is None or self.content_type is None
        ):
            raise ValueError(
                "nombre y content_type deben proporcionarse al sustituir el archivo"
            )
        return self
