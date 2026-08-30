"""
alembic/env.py
ERP-012: Alembic configuration for TOP WorX with synchronous PostgreSQL.

This uses the synchronous SQLAlchemy engine (same as the rest of the app)
so it integrates cleanly with the existing session.py.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Add backend/ to path so `app` imports resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

# ---------------------------------------------------------------------------
# Import ALL models here so Alembic can detect them for autogenerate.
# Add new model files to this list as you create them.
# ---------------------------------------------------------------------------
from app.db.base_class import Base  # noqa: F401 — needed for metadata

from app.models.user import User  # noqa: F401
from app.models.security import (  # noqa: F401
    Permission, Role, RolePermission, UserSession, AuditLog, TwoFactorAuth
)
# Add future models here:
# from app.models.inventory import InventoryItem, StockLevel, ...
# from app.models.hr import Employee, ...

# ---------------------------------------------------------------------------
# Alembic config
# ---------------------------------------------------------------------------
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (generate SQL script without a live DB).
    Useful for reviewing SQL before applying to production.
    Usage: alembic upgrade head --sql > migration.sql
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,  # Don't pool connections for migrations
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,              # Detect column type changes
            compare_server_default=True,    # Detect server default changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
