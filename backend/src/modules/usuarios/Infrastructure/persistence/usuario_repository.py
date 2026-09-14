from sqlalchemy import select

from modules.usuarios.domain.Entities.usuario import Correo, Departamento, Usuario
from modules.usuarios.domain.Enum.rol import Rol
from modules.usuarios.domain.Exceptions.excepciones import UsuarioNoEncontradoError
from modules.usuarios.Infrastructure.entities.usuario import UsuarioORM
from shared.uow import UnitOfWork


def to_domain(usuario_orm: UsuarioORM) -> Usuario:
    """Convierte la entidad ORM en la entidad de dominio, sin acoplar el
    dominio a SQLAlchemy."""
    return Usuario(
        id=usuario_orm.id,
        correo=Correo(usuario_orm.correo),
        rol=Rol(usuario_orm.rol),
        departamento=Departamento(usuario_orm.departamento),
        activo=usuario_orm.activo,
        creado_en=usuario_orm.creado_en,
        dado_de_baja_en=usuario_orm.dado_de_baja_en,
    )


def to_orm(usuario: Usuario) -> UsuarioORM:
    return UsuarioORM(
        id=usuario.id,
        correo=usuario.correo.valor,
        rol=usuario.rol.value,
        departamento=usuario.departamento.valor,
        activo=usuario.activo,
        creado_en=usuario.creado_en,
        dado_de_baja_en=usuario.dado_de_baja_en,
    )


class UsuarioRepositorySqlAlchemy:
    """Implementación del puerto `UsuarioRepository` sobre SQLAlchemy async.

    No hace commit: eso es responsabilidad de quien orqueste el `UnitOfWork`.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def guardar(self, usuario: Usuario) -> None:
        self.uow.session.add(to_orm(usuario))
        await self.uow.session.flush()

    async def obtener_por_correo(self, correo: str) -> Usuario | None:
        result = await self.uow.session.execute(
            select(UsuarioORM).where(UsuarioORM.correo == correo)
        )
        usuario_orm = result.scalar_one_or_none()
        return to_domain(usuario_orm) if usuario_orm is not None else None

    async def listar_activos(self) -> list[Usuario]:
        result = await self.uow.session.execute(
            select(UsuarioORM).where(UsuarioORM.activo.is_(True))
        )
        return [to_domain(usuario_orm) for usuario_orm in result.scalars().all()]

    async def actualizar(self, usuario: Usuario) -> None:
        usuario_orm = await self.uow.session.get(UsuarioORM, usuario.id)
        if usuario_orm is None:
            raise UsuarioNoEncontradoError(usuario.correo.valor)

        usuario_orm.rol = usuario.rol.value
        usuario_orm.departamento = usuario.departamento.valor
        usuario_orm.activo = usuario.activo
        usuario_orm.dado_de_baja_en = usuario.dado_de_baja_en
        await self.uow.session.flush()
