from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.archivos.infrastructure.db.persistence.documento_repository import (
    DocumentoRepositorySqlAlchemy,
)
from modules.mir.api.dto import ActualizarMirDTO, CrearMirDTO, MirDTO
from modules.mir.application.uses_cases.actualizar_mir import actualizar_mir
from modules.mir.application.uses_cases.buscar_por_nombre import obtener_por_codigo_mir
from modules.mir.application.uses_cases.crear_mir import crear_mir_con_archivos
from modules.mir.application.uses_cases.delete_mir import delete_mir
from modules.mir.application.uses_cases.list_all_mir import list_all_mir
from modules.mir.domain.exceptions.exceptions import (
    DatoObligatorioFaltanteError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.mir.infrastructure.db.persistance.mir_repository import (
    MirRepositorySqlAlchemy,
)
from shared.uow import UnitOfWork

router = APIRouter(prefix="/mir", tags=["MIR"])


def get_uow() -> UnitOfWork:
    return UnitOfWork()


def error_http(error: Exception) -> HTTPException:
    if isinstance(error, MirNoEncontradaError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "MIR no encontrada")
    if isinstance(error, EstadoInvalidoError):
        return HTTPException(status.HTTP_409_CONFLICT, "Estado de MIR no permitido")
    if isinstance(error, DatoObligatorioFaltanteError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error))
    return HTTPException(status.HTTP_502_BAD_GATEWAY, "No se pudo procesar la MIR")


@router.post("", response_model=MirDTO, status_code=status.HTTP_201_CREATED)
async def crear(
    datos: CrearMirDTO,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> MirDTO:
    try:
        mir = await crear_mir_con_archivos(
            codigo_mir=datos.codigo_mir,
            descripcion=datos.descripcion,
            tipo=datos.tipo,
            detectada_por_id=datos.detectada_por_id,
            solucionado=datos.solucionado,
            prioridad=datos.prioridad,
            solucion_adoptada=datos.solucion_adoptada,
            analisis_causas=datos.analisis_causas,
            algo_mas_que_hacer=datos.algo_mas_que_hacer,
            adjuntos=[],
            storage=None,
            documento_repositorio=DocumentoRepositorySqlAlchemy(uow),
            mir_repositorio=MirRepositorySqlAlchemy(uow),
            uow=uow,
        )
    except Exception as error:
        raise error_http(error) from error
    return MirDTO.from_dominio(mir)


@router.get("", response_model=list[MirDTO])
async def listar(uow: Annotated[UnitOfWork, Depends(get_uow)]) -> list[MirDTO]:
    async with uow:
        mirs = await list_all_mir(MirRepositorySqlAlchemy(uow))
        return [MirDTO.from_dominio(mir) for mir in mirs]


@router.get("/{codigo_mir}", response_model=MirDTO)
async def consultar(
    codigo_mir: str, uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> MirDTO:
    async with uow:
        mir = await obtener_por_codigo_mir(codigo_mir, MirRepositorySqlAlchemy(uow))
        if mir is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "MIR no encontrada")
        return MirDTO.from_dominio(mir)


@router.patch("/{mir_id}", response_model=MirDTO)
async def actualizar(
    mir_id: UUID,
    datos: ActualizarMirDTO,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> MirDTO:
    async with uow:
        try:
            mir = await actualizar_mir(
                MirRepositorySqlAlchemy(uow),
                mir_id,
                descripcion=datos.descripcion,
                tipo=datos.tipo,
                prioridad=datos.prioridad,
                solucionado=datos.solucionado,
                solucion_adoptada=datos.solucion_adoptada,
                analisis_causas=datos.analisis_causas,
                algo_mas_que_hacer=datos.algo_mas_que_hacer,
            )
        except (
            MirNoEncontradaError,
            EstadoInvalidoError,
            DatoObligatorioFaltanteError,
        ) as error:
            raise error_http(error) from error
        await uow.commit()
        return MirDTO.from_dominio(mir)


@router.delete("/{mir_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dar_de_baja(
    mir_id: UUID,
    actor_id: UUID,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> None:
    # actor_id lo declara el cliente; sustituir por identidad verificada al integrar autenticacion.
    async with uow:
        try:
            await delete_mir(mir_id, MirRepositorySqlAlchemy(uow), actor_id=actor_id)
        except (MirNoEncontradaError, EstadoInvalidoError) as error:
            raise error_http(error) from error
        await uow.commit()
