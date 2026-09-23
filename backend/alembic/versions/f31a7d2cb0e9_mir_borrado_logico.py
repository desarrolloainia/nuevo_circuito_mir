"""Añade la baja lógica y su traza a las MIR existentes.

Revision ID: f31a7d2cb0e9
Revises: d2ada575cfde
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f31a7d2cb0e9"
down_revision: str | Sequence[str] | None = "d2ada575cfde"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "mirs",
        sa.Column("borrado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("mirs", sa.Column("borrado_por_id", sa.Uuid(), nullable=True))
    op.add_column(
        "mirs", sa.Column("borrado_en", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    raise NotImplementedError("No se puede eliminar el historial de bajas de MIR")
