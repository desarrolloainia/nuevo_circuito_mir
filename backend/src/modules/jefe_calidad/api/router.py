from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.jefe_calidad.application.asignar_responsable import (
    UsuarioNoEsTecnicoCldError,
    asignar_responsable,
)
from modules.jefe_calidad.application.denegar_mir import denegar_mir
from modules.jefe_calidad.application.listar_mir_en_revision import (
    listar_mir_en_revision,
)
from modules.mir.api.dto import AsignarTecnicoCldDTO, DenegarMirDTO, MirDTO
from modules.mir.api.router import error_http, get_uow
from modules.mir.domain.exceptions.exceptions import (
    ActorNoAutorizadoError,
    EstadoInvalidoError,
    MirNoEncontradaError,
)
from modules.mir.infrastructure.db.persistance.mir_repository import (
    MirRepositorySqlAlchemy,
)
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from modules.usuarios.Infrastructure.persistence.usuario_repository import (
    UsuarioRepositorySqlAlchemy,
)
from shared.uow import UnitOfWork

router = APIRouter(prefix="/jefe-calidad/mir", tags=["Jefe de calidad"])


@router.get("", response_model=list[MirDTO])
async def listar(uow: Annotated[UnitOfWork, Depends(get_uow)]) -> list[MirDTO]:
    async with uow:
        mirs = await listar_mir_en_revision(MirRepositorySqlAlchemy(uow))
        return [MirDTO.from_dominio(mir) for mir in mirs]


@router.post("/{mir_id}/asignar-tecnico", response_model=MirDTO)
async def asignar_tecnico(
    mir_id: UUID,
    datos: AsignarTecnicoCldDTO,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> MirDTO:
    async with uow:
        try:
            mir = await asignar_responsable(
                MirRepositorySqlAlchemy(uow),
                UsuarioRepositorySqlAlchemy(uow),
                mir_id,
                datos.tecnico_cld_id,
            )
        except UsuarioNoEncontradoError as error:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Usuario no encontrado"
            ) from error
        except UsuarioNoEsTecnicoCldError as error:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "El usuario no es tecnico de CLD",
            ) from error
        except (MirNoEncontradaError, EstadoInvalidoError) as error:
            raise error_http(error) from error
        await uow.commit()
        return MirDTO.from_dominio(mir)


@router.post("/{mir_id}/denegar", response_model=MirDTO)
async def denegar(
    mir_id: UUID,
    datos: DenegarMirDTO,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> MirDTO:
    # actor_id lo declara el cliente; sustituir por identidad verificada al integrar autenticacion.
    async with uow:
        try:
            mir = await denegar_mir(
                MirRepositorySqlAlchemy(uow),
                UsuarioRepositorySqlAlchemy(uow),
                mir_id,
                datos.actor_id,
            )
        except (
            MirNoEncontradaError,
            EstadoInvalidoError,
            ActorNoAutorizadoError,
        ) as error:
            raise error_http(error) from error
        await uow.commit()
        return MirDTO.from_dominio(mir)
