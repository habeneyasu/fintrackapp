from logging.config import fileConfig
from urllib.parse import quote_plus
from sqlalchemy import pool
from alembic import context
from sqlalchemy import engine_from_config
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base import Base  # Must import all models through this

config = context.config

# URL-encode password and escape % for configparser
encoded_password = quote_plus(settings.DB_PASSWORD).replace('%', '%%')
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# CRITICAL: Set metadata for autogenerate
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
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
            compare_server_default=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()