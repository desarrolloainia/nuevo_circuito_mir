from datetime import datetime

from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


## Esto se obtinene atraves de las variables de entorno
class SharePointSettings(BaseSettings):
    """Configuracion del App Registration y del drive de SharePoint destino."""

    model_config = SettingsConfigDict(env_prefix="SHAREPOINT_")

    tenant_id: str
    client_id: str
    client_secret: SecretStr
    drive_id: str
    root_folder_item_id: str = "root"


class DriveItemSchema(BaseModel):
    """Subconjunto tipado del driveItem de Microsoft Graph que necesita esta app."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str | None = None
    size: int | None = None
    web_url: str | None = None
    created_date_time: datetime | None = None
    last_modified_date_time: datetime | None = None


class GraphErrorDetail(BaseModel):
    """Normaliza el cuerpo de error (ODataError.error) devuelto por Graph."""

    code: str | None = None
    message: str | None = None
