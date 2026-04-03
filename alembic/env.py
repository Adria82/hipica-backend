from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Añadir el raíz del proyecto al path para que funcione el import de app.*
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar todos los modelos para que SQLModel los registre en metadata.
# El orden importa: primero los modelos sin FK, luego los que tienen FK.
import app.models  # noqa: F401 — registra Stable, User, Level, Track, Box, Horse, Lesson, etc.

from app.core.config import DATABASE_URL

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Apuntar al metadata de SQLModel (todas las tablas declaradas con table=True)
target_metadata = SQLModel.metadata

# Sobrescribir la URL con la del proyecto (ignora el valor de alembic.ini)
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
