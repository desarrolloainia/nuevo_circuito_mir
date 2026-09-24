from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from modules.archivos.infrastructure.db.entities.documento import DocumentoORM
from modules.archivos.infrastructure.db.persistence.documento_repository import (
    to_domain as documento_to_domain,
)
from modules.mir.domain.entities.mir import MIR
from modules.mir.domain.Enum.estado import Estado
from modules.mir.infrastructure.db.entities.contadorcodigo import MIRCodigoContadorModel
from modules.mir.infrastructure.db.entities.mir import MirOrm
from shared.uow import UnitOfWork


def to_domain(mir_orm: MirOrm) -> MIR:
    """Convierte una entidad ORM en una entidad de dominio.

    Mantiene desacoplada la capa de persistencia de la capa de dominio,
    evitando que el dominio dependa directamente de SQLAlchemy.
    """
    return MIR(
        id=mir_orm.id,
        codigo_mir=mir_orm.codigo_mir,
        descripcion=mir_orm.descripcion,
        tipo=mir_orm.tipo,
        estado=mir_orm.estado,
        detectada_por_id=mir_orm.detectada_por_id,
        solucionado=mir_orm.solucionado,
        solucion_adoptada=mir_orm.solucion_adoptada,
        analisis_causas=mir_orm.analisis_causas,
        algo_mas_que_hacer=mir_orm.algo_mas_que_hacer,
        prioridad=mir_orm.prioridad,
        tecnico_cld_id=mir_orm.tecnico_cld_id,
        responsable_resolucion_id=mir_orm.responsable_resolucion_id,
        ejecutor_id=mir_orm.ejecutor_id,
        fecha_prevista_resolucion=mir_orm.fecha_prevista_resolucion,
        fecha_comprobacion_eficacia=mir_orm.fecha_comprobacion_eficacia,
        resultado_comprobacion_eficacia=mir_orm.resultado_comprobacion_eficacia,
        documentos=[documento_to_domain(doc) for doc in mir_orm.archivos_adjuntos],
        fecha_deteccion=mir_orm.fecha_deteccion,
        empresa_nombre=mir_orm.empresa_nombre,
        persona_contacto=mir_orm.persona_contacto,
        telefono=mir_orm.telefono,
        correo_electronico=mir_orm.correo_electronico,
        nombre_comercial=mir_orm.nombre_comercial,
        codigo_cliente=mir_orm.codigo_cliente,
        creado_en=mir_orm.creado_en,
        modificado_en=mir_orm.modificado_en,
        borrado=mir_orm.borrado,
        borrado_por_id=mir_orm.borrado_por_id,
        borrado_en=mir_orm.borrado_en,
    )


def to_orm(mir: MIR) -> MirOrm:
    """Convierte una entidad de dominio en una entidad ORM.

    Transforma el modelo de dominio al modelo utilizado por
    infraestructura para persistirlo en base de datos.
    """
    return MirOrm(
        id=mir.id,
        codigo_mir=mir.codigo_mir,
        descripcion=mir.descripcion,
        tipo=mir.tipo,
        estado=mir.estado,
        detectada_por_id=mir.detectada_por_id,
        solucionado=mir.solucionado,
        solucion_adoptada=mir.solucion_adoptada,
        analisis_causas=mir.analisis_causas,
        algo_mas_que_hacer=mir.algo_mas_que_hacer,
        prioridad=mir.prioridad,
        tecnico_cld_id=mir.tecnico_cld_id,
        responsable_resolucion_id=mir.responsable_resolucion_id,
        ejecutor_id=mir.ejecutor_id,
        fecha_prevista_resolucion=mir.fecha_prevista_resolucion,
        fecha_comprobacion_eficacia=mir.fecha_comprobacion_eficacia,
        resultado_comprobacion_eficacia=mir.resultado_comprobacion_eficacia,
        archivos_adjuntos=[],
        fecha_deteccion=mir.fecha_deteccion,
        empresa_nombre=mir.empresa_nombre,
        persona_contacto=mir.persona_contacto,
        telefono=mir.telefono,
        correo_electronico=mir.correo_electronico,
        nombre_comercial=mir.nombre_comercial,
        codigo_cliente=mir.codigo_cliente,
        creado_en=mir.creado_en,
        modificado_en=mir.modificado_en,
        borrado=mir.borrado,
        borrado_por_id=mir.borrado_por_id,
        borrado_en=mir.borrado_en,
    )


class MirRepositorySqlAlchemy:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow: UnitOfWork = uow

    async def create_mir(self, mir: MIR) -> MIR:
        mir_orm = to_orm(mir)
        for documento in mir.documentos:
            documento_orm = await self.uow.session.get(DocumentoORM, documento.id)
            if documento_orm is None:
                raise ValueError("Documento no encontrado")
            mir_orm.archivos_adjuntos.append(documento_orm)
        self.uow.session.add(mir_orm)
        await self.uow.session.flush()
        return mir

    async def reservar_numero(self, anio: int) -> int:
        sentencia = insert(MIRCodigoContadorModel).values(anio=anio, ultimo_numero=1)
        sentencia = sentencia.on_conflict_do_update(
            index_elements=[MIRCodigoContadorModel.anio],
            set_={"ultimo_numero": MIRCodigoContadorModel.ultimo_numero + 1},
        ).returning(MIRCodigoContadorModel.ultimo_numero)
        return int((await self.uow.session.execute(sentencia)).scalar_one())

    async def get_mir_all(self, detectada_por_id: UUID | None = None) -> list[MIR]:
        consulta = select(MirOrm).where(MirOrm.borrado.is_(False))
        if detectada_por_id is not None:
            consulta = consulta.where(MirOrm.detectada_por_id == detectada_por_id)
        result = await self.uow.session.execute(
            consulta.order_by(MirOrm.creado_en.desc())
        )
        return [to_domain(mir_orm) for mir_orm in result.scalars().all()]

    async def filtrar_estado(self, estado: Estado) -> list[MIR]:
        result = await self.uow.session.execute(
            select(MirOrm)
            .where(MirOrm.estado == estado, MirOrm.borrado.is_(False))
            .order_by(MirOrm.creado_en.desc())
        )
        return [to_domain(mir_orm) for mir_orm in result.scalars().all()]

    async def editar_estado(self, mir_id: UUID, estado: Estado) -> MIR:
        mir_orm = await self.uow.session.get(MirOrm, mir_id)
        if mir_orm is None:
            raise ValueError(f"MIR con id {mir_id} no encontrada")
        mir_orm.estado = estado
        mir_orm.modificado_en = datetime.now(UTC)
        await self.uow.session.flush()
        return to_domain(mir_orm)

    async def get_by_id(self, mir_id: UUID) -> MIR | None:
        mir_orm = await self.uow.session.get(MirOrm, mir_id)
        return to_domain(mir_orm) if mir_orm and not mir_orm.borrado else None

    async def get_by_codigo_mir(self, codigo_mir: str) -> MIR | None:
        result = await self.uow.session.execute(
            select(MirOrm).where(
                MirOrm.codigo_mir == codigo_mir, MirOrm.borrado.is_(False)
            )
        )
        mir_orm = result.scalar_one_or_none()
        return to_domain(mir_orm) if mir_orm else None

    async def update_mir(self, mir: MIR) -> MIR:
        mir_orm = await self.uow.session.get(MirOrm, mir.id)
        if mir_orm is None:
            raise ValueError(f"MIR con id {mir.id} no encontrada")

        mir_orm.descripcion = mir.descripcion
        mir_orm.tipo = mir.tipo
        mir_orm.estado = mir.estado
        mir_orm.detectada_por_id = mir.detectada_por_id
        mir_orm.solucionado = mir.solucionado
        mir_orm.solucion_adoptada = mir.solucion_adoptada
        mir_orm.analisis_causas = mir.analisis_causas
        mir_orm.algo_mas_que_hacer = mir.algo_mas_que_hacer
        mir_orm.prioridad = mir.prioridad
        mir_orm.tecnico_cld_id = mir.tecnico_cld_id
        mir_orm.responsable_resolucion_id = mir.responsable_resolucion_id
        mir_orm.ejecutor_id = mir.ejecutor_id
        mir_orm.fecha_prevista_resolucion = mir.fecha_prevista_resolucion
        mir_orm.fecha_comprobacion_eficacia = mir.fecha_comprobacion_eficacia
        mir_orm.resultado_comprobacion_eficacia = mir.resultado_comprobacion_eficacia
        mir_orm.fecha_deteccion = mir.fecha_deteccion
        mir_orm.empresa_nombre = mir.empresa_nombre
        mir_orm.persona_contacto = mir.persona_contacto
        mir_orm.telefono = mir.telefono
        mir_orm.correo_electronico = mir.correo_electronico
        mir_orm.nombre_comercial = mir.nombre_comercial
        mir_orm.codigo_cliente = mir.codigo_cliente
        mir_orm.borrado = mir.borrado
        mir_orm.borrado_por_id = mir.borrado_por_id
        mir_orm.borrado_en = mir.borrado_en
        mir_orm.modificado_en = datetime.now(UTC)

        await self.uow.session.flush()
        return to_domain(mir_orm)

    async def delete_mir(self, mir_id: UUID, actor_id: UUID) -> None:
        mir = await self.get_by_id(mir_id)
        if mir is None:
            return
        mir.dar_de_baja(actor_id)
        _ = await self.update_mir(mir)

    async def aumentar_codigo_mir(self, codigo_mir: str) -> str:
        """Aumenta el código MIR manteniendo el año.

        Ejemplo:
            26001 -> 26002
            26099 -> 26100
        """
        year = codigo_mir[:2]
        sequence = codigo_mir[2:]

        new_sequence = int(sequence) + 1

        return f"{year}{new_sequence:03d}"
