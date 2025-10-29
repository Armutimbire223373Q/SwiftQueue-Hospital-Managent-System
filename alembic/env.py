import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context

# Ensure backend is importable so we can access models/metadata
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'backend'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

import app.database as database
# Import all model files to ensure Alembic detects all tables
from app.models import models  # Main models (includes new Prescription, Inventory, Portal models)
from app.models import workflow_models  # Workflow models
from app.models import staff_models  # Staff and department models
from app.models import file_models  # File management models

target_metadata = database.Base.metadata


def get_db_url_from_env():
    # Prefer DATABASE_URL, then SQLALCHEMY_DATABASE_URL, then alembic.ini
    return os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URL') or config.get_main_option('sqlalchemy.url')


def run_migrations_offline():
    url = get_db_url_from_env()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Ensure the alembic config has the right URL (allow env var to override)
    db_url = get_db_url_from_env()
    if db_url:
        config.set_main_option('sqlalchemy.url', db_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
