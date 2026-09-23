from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.config import Base, settings
import app.models  # Ensures User and Item models are loaded into Base.metadata

# Alembic Config object
config = context.config

# Escape '%' characters for ConfigParser compatibility and inject DATABASE_URL
if settings.DATABASE_URL:
    escaped_db_url = settings.DATABASE_URL
    config.set_main_option("sqlalchemy.url", escaped_db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts directly without requiring an active database connection.
    """
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an engine and connects directly to the target database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()