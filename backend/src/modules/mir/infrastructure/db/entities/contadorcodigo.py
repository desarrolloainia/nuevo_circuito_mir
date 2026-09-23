from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class MIRCodigoContadorModel(Base):
    __tablename__ = "mir_codigo_contadores"

    anio: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    ultimo_numero: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
