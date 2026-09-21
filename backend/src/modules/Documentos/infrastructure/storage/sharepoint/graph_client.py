from azure.identity.aio import ClientSecretCredential
from kiota_abstractions.headers_collection import HeadersCollection
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.content.content_request_builder import (
    ContentRequestBuilder,
)
from msgraph.generated.models.drive_item import DriveItem

from .schema import SharePointSettings

GRAPH_SCOPES = ["https://graph.microsoft.com/.default"]


class SharePointGraphClient:
    """Centraliza todas las llamadas al SDK de Microsoft Graph contra un drive de SharePoint."""

    def __init__(self, settings: SharePointSettings) -> None:
        credential = ClientSecretCredential(
            tenant_id=settings.tenant_id,
            client_id=settings.client_id,
            client_secret=settings.client_secret.get_secret_value(),
        )
        self._client = GraphServiceClient(credentials=credential, scopes=GRAPH_SCOPES)
        self._drive_id = settings.drive_id
        self._root_folder_item_id = settings.root_folder_item_id

    def _item(self, item_id: str):
        return self._client.drives.by_drive_id(self._drive_id).items.by_drive_item_id(item_id)

    async def upload_content(self, filename: str, content: bytes, content_type: str) -> DriveItem:
        item_path = f"{self._root_folder_item_id}:/{filename}:"
        headers = HeadersCollection()
        headers.add("Content-Type", content_type)
        request_configuration = ContentRequestBuilder.ContentRequestBuilderPutRequestConfiguration(
            headers=headers
        )
        drive_item = await self._item(item_path).content.put(
            content, request_configuration=request_configuration
        )
        if drive_item is None:
            raise RuntimeError("Microsoft Graph no devolvio el driveItem tras la subida")
        return drive_item

    async def get_documentos(self) -> list[DriveItem]:
        items = await self._client.drives.by_drive_id(self._drive_id).items.by_drive_item_id(self._root_folder_item_id).children.get()
        if items is None:
            raise RuntimeError("Microsoft Graph no devolvio items para el root folder")
        return items.value or []

    async def download_content(self, item_id: str) -> bytes:
        content = await self._item(item_id).content.get()
        if content is None:
            raise RuntimeError("Microsoft Graph no devolvio contenido para el driveItem")
        return content

    async def delete_item(self, item_id: str) -> None:
        await self._item(item_id).delete()
