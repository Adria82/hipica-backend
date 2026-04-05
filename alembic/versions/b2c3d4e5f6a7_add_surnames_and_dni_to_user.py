"""add_surnames_and_dni_to_user

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-05 00:00:00.000000

Añade las columnas `apellidos` y `dni` a la tabla `user`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("apellidos", sa.String(), nullable=True))
    op.add_column("user", sa.Column("dni", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "dni")
    op.drop_column("user", "apellidos")
