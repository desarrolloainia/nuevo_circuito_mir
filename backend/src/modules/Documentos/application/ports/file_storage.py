from dataclasses import dataclass
from typing import Protocol


## Representa el archivo que subimos a sharepoint o a cualquier otro storage
@dataclass
class ArchivoSubido:
    storage_id: str
    nombre: str
    tamano_bytes: int
    url: str | None = None


class FileStorageError(Exception):
    pass


class FileStorageNotFoundError(FileStorageError):
    pass


class FileStorageAuthError(FileStorageError):
    pass


class FileStorageRateLimitedError(FileStorageError):
    pass


class FileStoragePort(Protocol):
    async def subir(self, nombre: str, contenido: bytes, content_type: str) -> ArchivoSubido: ...

    async def eliminar(self, storage_id: str) -> None: ...

    async def descargar(self, storage_id: str) -> bytes: ...
