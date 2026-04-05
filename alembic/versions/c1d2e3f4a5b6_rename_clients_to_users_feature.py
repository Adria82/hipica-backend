"""rename CLIENTS to USERS feature code

Revision ID: c1d2e3f4a5b6
Revises: 0b4c25361aa2
Create Date: 2026-04-05 13:30:00.000000

Renombra el código de funcionalidad CLIENTS → USERS en la tabla stablefeature,
reflejando que el módulo gestiona usuarios de la hípica, no solo clientes.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "0b4c25361aa2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Convertir la columna a texto para poder manipular el enum libremente
    op.execute("ALTER TABLE stablefeature ALTER COLUMN feature TYPE varchar USING feature::varchar")
    # 2. Renombrar el valor en los datos existentes
    op.execute("UPDATE stablefeature SET feature = 'USERS' WHERE feature = 'CLIENTS'")
    # 3. Eliminar el tipo enum antiguo y recrearlo con el nuevo valor
    op.execute("DROP TYPE featurecode")
    op.execute("CREATE TYPE featurecode AS ENUM ('HORSES','USERS','LESSONS','BOOKINGS','BILLING','REPORTING')")
    # 4. Volver a tipar la columna con el enum actualizado
    op.execute("ALTER TABLE stablefeature ALTER COLUMN feature TYPE featurecode USING feature::featurecode")


def downgrade() -> None:
    op.execute("ALTER TABLE stablefeature ALTER COLUMN feature TYPE varchar USING feature::varchar")
    op.execute("UPDATE stablefeature SET feature = 'CLIENTS' WHERE feature = 'USERS'")
    op.execute("DROP TYPE featurecode")
    op.execute("CREATE TYPE featurecode AS ENUM ('HORSES','CLIENTS','LESSONS','BOOKINGS','BILLING','REPORTING')")
    op.execute("ALTER TABLE stablefeature ALTER COLUMN feature TYPE featurecode USING feature::featurecode")
