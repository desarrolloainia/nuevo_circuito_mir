"""crear tabla usuarios

Revision ID: 1ad451f3955c
Revises:
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "1ad451f3955c"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("correo", sa.String(), nullable=False),
        sa.Column("rol", sa.String(), nullable=False),
        sa.Column("departamento", sa.String(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dado_de_baja_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_usuarios_correo"), "usuarios", ["correo"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_usuarios_correo"), table_name="usuarios")
    op.drop_table("usuarios")
