"""Carga previa de un documento, con dobles manuales y sin SharePoint real."""

import asyncio
import logging
from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest
from modules.archivos.domain.excepciones import (
    ArchivoDemasiadoGrandeError,
    CreadorNoEncontradoError,
    DocumentoInvalidoError,
)

from modules.archivos.application.ports.file_storage import (
    ArchivoSubido,
    FileStorageError,
)
from modules.archivos.application.uses_cases.subir_documento import subir_documento
from modules.archivos.domain.entities.documento import (
    TAMANO_MAXIMO_BYTES,
    Documento,
)
from modules.archivos.domain.Enum.estado_documetno import TipoDocumento

NOMBRE = "evidencia-ficticia.pdf"
CONTENIDO = b"contenido de prueba"


class StorageFalso:
    def __init__(self, fallar: bool = False) -> None:
        self.fallar = fallar
        self.subidos: list[str] = []
        self.eliminados: list[str] = []

    async def subir(
        self, nombre: str, contenido: bytes, content_type: str
    ) -> ArchivoSubido:
        if self.fallar:
            raise FileStorageError("almacenamiento no disponible")
        self.subidos.append(nombre)
        return ArchivoSubido(
            storage_id=f"remoto-{len(self.subidos)}",
            nombre=nombre,
            tamano_bytes=len(contenido),
        )

    async def eliminar(self, storage_id: str) -> None:
        self.eliminados.append(storage_id)

    async def descargar(self, storage_id: str) -> bytes:
        return CONTENIDO


class DocumentoRepositorioFalso:
    def __init__(self, fallar: bool = False) -> None:
        self.documentos: dict[UUID, Documento] = {}
        self.fallar = fallar

    async def save(self, documento: Documento) -> Documento:
        if self.fallar:
            raise RuntimeError("fallo simulado de persistencia")
        self.documentos[documento.id] = documento
        return documento

    async def update(self, documento: Documento) -> Documento:
        self.documentos[documento.id] = documento
        return documento

    async def get_all(self) -> list[Documento]:
        return list(self.documentos.values())

    async def delete(self, documento_id: UUID) -> None:
        _ = self.documentos.pop(documento_id, None)

    async def get_by_id(self, documento_id: UUID) -> Documento | None:
        return self.documentos.get(documento_id)

    async def bloquear(self, documento_ids: Sequence[UUID]) -> dict[UUID, UUID | None]:
        return {
            documento_id: self.documentos[documento_id].mir_id
            for documento_id in documento_ids
            if documento_id in self.documentos
        }

    async def vincular(self, documento_ids: Sequence[UUID], mir_id: UUID) -> None:
        for documento_id in documento_ids:
            self.documentos[documento_id].mir_id = mir_id


class ConsultaCreadoresFalsa:
    def __init__(self, existentes: Sequence[UUID] = ()) -> None:
        self.existentes: set[UUID] = set(existentes)

    async def existe(self, creador_id: UUID) -> bool:
        return creador_id in self.existentes


class UnidadTrabajoFalsa:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


class Escenario:
    def __init__(self, storage_falla: bool = False, repo_falla: bool = False) -> None:
        self.creador_id = uuid4()
        self.storage = StorageFalso(fallar=storage_falla)
        self.repositorio = DocumentoRepositorioFalso(fallar=repo_falla)
        self.creadores = ConsultaCreadoresFalsa([self.creador_id])
        self.uow = UnidadTrabajoFalsa()

    async def subir(self, **cambios: object) -> Documento:
        datos: dict[str, object] = {
            "nombre": NOMBRE,
            "contenido": CONTENIDO,
            "content_type": "application/pdf",
            "tipo": TipoDocumento.PDF,
            "creado_por": self.creador_id,
        }
        datos.update(cambios)
        return await subir_documento(
            **datos,  # pyright: ignore[reportArgumentType] - datos tipados en la llamada
            storage=self.storage,
            repositorio=self.repositorio,
            creadores=self.creadores,
            uow=self.uow,
        )


def test_una_carga_valida_guarda_el_tamano_y_conserva_el_nombre_original():
    async def caso() -> None:
        escenario = Escenario()

        documento = await escenario.subir()

        assert documento.nombre == NOMBRE
        assert documento.tamano_bytes == len(CONTENIDO)
        assert documento.mir_id is None
        assert escenario.uow.commits == 1
        # El nombre remoto no reproduce el del usuario.
        assert NOMBRE not in escenario.storage.subidos[0]

    asyncio.run(caso())


def test_un_creador_inexistente_impide_subir_el_archivo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(CreadorNoEncontradoError):
            _ = await escenario.subir(creado_por=uuid4())

        assert escenario.storage.subidos == []

    asyncio.run(caso())


def test_un_nombre_o_un_contenido_vacios_impiden_subir_el_archivo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(DocumentoInvalidoError):
            _ = await escenario.subir(nombre="   ")
        with pytest.raises(DocumentoInvalidoError):
            _ = await escenario.subir(contenido=b"")

        assert escenario.storage.subidos == []

    asyncio.run(caso())


def test_un_archivo_mayor_del_limite_se_rechaza_antes_de_subirlo():
    async def caso() -> None:
        escenario = Escenario()

        with pytest.raises(ArchivoDemasiadoGrandeError):
            _ = await escenario.subir(contenido=b"x" * (TAMANO_MAXIMO_BYTES + 1))

        assert escenario.storage.subidos == []

    asyncio.run(caso())


def test_el_limite_exacto_se_acepta():
    async def caso() -> None:
        escenario = Escenario()

        documento = await escenario.subir(contenido=b"x" * TAMANO_MAXIMO_BYTES)

        assert documento.tamano_bytes == TAMANO_MAXIMO_BYTES

    asyncio.run(caso())


def test_un_fallo_al_guardar_revierte_el_archivo_y_no_registra_datos_sensibles(
    caplog: pytest.LogCaptureFixture,
):
    async def caso() -> None:
        escenario = Escenario(repo_falla=True)

        with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError):
            _ = await escenario.subir()

        assert escenario.storage.eliminados == ["remoto-1"]
        registros = caplog.text
        assert NOMBRE not in registros
        assert "remoto-1" not in registros

    asyncio.run(caso())
