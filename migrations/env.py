
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the shared database configuration
from app.database import Base, DATABASE_URL

# Register all SQLAlchemy models with Base.metadata
from app import models
from app import order_models
from app import user_models


# Alembic configuration object
config = context.config

# Configure logging using alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used to detect database changes
target_metadata = Base.metadata

# Use the application's database connection URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Generate SQL migration statements without
    connecting directly to the database.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    Connect to PostgreSQL and execute migrations
    directly against the database.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section, {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which migration mode Alembic should use
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
