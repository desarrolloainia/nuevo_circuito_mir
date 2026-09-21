from fastapi import APIRouter, Depends, HTTPException, status

from modules.usuarios.api.dto import (
    ActualizarUsuarioDTO,
    RegistrarUsuarioDTO,
    UsuarioRead,
)
from modules.usuarios.application.uses_cases.actualizar_usuario import (
    actualizar_usuario,
)
from modules.usuarios.application.uses_cases.consultar_usuario import (
    consultar_usuario,
)
from modules.usuarios.application.uses_cases.dar_baja_usuario import dar_baja_usuario
from modules.usuarios.application.uses_cases.listar_usuarios import listar_usuarios
from modules.usuarios.application.uses_cases.registrar_usuario import (
    registrar_usuario,
)
from modules.usuarios.domain.Exceptions.excepciones import (
    CorreoYaRegistradoError,
    DatoObligatorioFaltanteError,
    FormatoCorreoInvalidoError,
    RolInvalidoError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from modules.usuarios.Infrastructure.persistence.usuario_repository import (
    UsuarioRepositorySqlAlchemy,
)
from shared.uow import UnitOfWork

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

_ERRORES_HTTP: dict[type[Exception], int] = {
    CorreoYaRegistradoError: status.HTTP_409_CONFLICT,
    UsuarioInactivoError: status.HTTP_409_CONFLICT,
    UsuarioNoEncontradoError: status.HTTP_404_NOT_FOUND,
    RolInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    FormatoCorreoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DatoObligatorioFaltanteError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def get_uow() -> UnitOfWork:
    return UnitOfWork()


def error_http(error: Exception) -> HTTPException:
    codigo = _ERRORES_HTTP.get(type(error), status.HTTP_502_BAD_GATEWAY)
    return HTTPException(codigo, str(error))


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos: RegistrarUsuarioDTO,
    uow: UnitOfWork = Depends(get_uow),
) -> UsuarioRead:
    async with uow:
        repo = UsuarioRepositorySqlAlchemy(uow)
        try:
            usuario = await registrar_usuario(
                repo=repo,
                nombre=datos.nombre,
                correo=datos.correo,
                rol=datos.rol,
                departamento=datos.departamento,
            )
        except Exception as error:
            raise error_http(error) from error
        await uow.commit()
    return UsuarioRead.from_dominio(usuario)


@router.get("", response_model=list[UsuarioRead])
async def listar_usuarios_activos(
    uow: UnitOfWork = Depends(get_uow),
) -> list[UsuarioRead]:
    async with uow:
        repo = UsuarioRepositorySqlAlchemy(uow)
        usuarios = await listar_usuarios(repo=repo)
    return [UsuarioRead.from_dominio(usuario) for usuario in usuarios]


@router.get("/{correo}", response_model=UsuarioRead)
async def consultar_usuario_por_correo(
    correo: str,
    uow: UnitOfWork = Depends(get_uow),
) -> UsuarioRead:
    async with uow:
        repo = UsuarioRepositorySqlAlchemy(uow)
        try:
            usuario = await consultar_usuario(repo=repo, correo=correo)
        except Exception as error:
            raise error_http(error) from error
    return UsuarioRead.from_dominio(usuario)


@router.patch("/{correo}", response_model=UsuarioRead)
async def actualizar_usuario_existente(
    correo: str,
    datos: ActualizarUsuarioDTO,
    uow: UnitOfWork = Depends(get_uow),
) -> UsuarioRead:
    async with uow:
        repo = UsuarioRepositorySqlAlchemy(uow)
        try:
            usuario = await actualizar_usuario(
                repo=repo,
                correo=correo,
                nombre=datos.nombre,
                rol=datos.rol,
                departamento=datos.departamento,
            )
        except Exception as error:
            raise error_http(error) from error
        await uow.commit()
    return UsuarioRead.from_dominio(usuario)


@router.delete("/{correo}", status_code=status.HTTP_204_NO_CONTENT)
async def dar_baja_usuario_existente(
    correo: str,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    async with uow:
        repo = UsuarioRepositorySqlAlchemy(uow)
        try:
            await dar_baja_usuario(repo=repo, correo=correo)
        except Exception as error:
            raise error_http(error) from error
        await uow.commit()
