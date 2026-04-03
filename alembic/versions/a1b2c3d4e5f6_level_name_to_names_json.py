"""level_name_to_names_json

Revision ID: a1b2c3d4e5f6
Revises: 4c21be75e493
Create Date: 2026-04-03 18:00:00.000000

Convierte la columna `name` (str) de la tabla `level`
a `names` (JSON) para soporte multiidioma.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4c21be75e493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Reemplaza columna name (str) por names (JSON)."""
    # Añadir nueva columna names (nullable temporalmente)
    op.add_column('level', sa.Column('names', JSON(), nullable=True))

    # Migrar datos existentes: name → {"es": name, "en": name, "ca": name}
    op.execute(
        "UPDATE level SET names = json_build_object('es', name, 'en', name, 'ca', name)"
    )

    # Hacer names NOT NULL ahora que tiene datos
    op.alter_column('level', 'names', nullable=False)

    # Eliminar columna antigua
    op.drop_index('ix_level_name', table_name='level', if_exists=True)
    op.drop_column('level', 'name')


def downgrade() -> None:
    """Restaura columna name (str) desde names JSON."""
    # Añadir columna name de vuelta (nullable temporalmente)
    op.add_column('level', sa.Column('name', sa.String(), nullable=True))

    # Restaurar datos: usar valor 'es' del JSON, o primer valor disponible
    op.execute(
        "UPDATE level SET name = COALESCE(names->>'es', names->>'ca', names->>'en', 'nivel')"
    )

    # Hacer name NOT NULL
    op.alter_column('level', 'name', nullable=False)

    # Recrear índice único
    op.create_index('ix_level_name', 'level', ['name'], unique=True)

    # Eliminar columna names
    op.drop_column('level', 'names')
