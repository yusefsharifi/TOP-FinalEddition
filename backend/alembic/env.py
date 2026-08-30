"""
backend/alembic/env.py
Alembic migration environment.
Reads DATABASE_URL from app.core.config.settings so credentials
never appear in alembic.ini.
"""
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Make sure the app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

# All models must be imported here so Alembic sees them for autogenerate
from app.db.base_class import Base  # noqa: F401
import app.models.user              # noqa: F401
import app.models.security          # noqa: F401
import app.models.finance           # noqa: F401
import app.models.inventory         # noqa: F401
import app.models.sales             # noqa: F401
import app.models.procurement       # noqa: F401
import app.models.hr                # noqa: F401
import app.models.bi                # noqa: F401
import app.models.crm               # noqa: F401
import app.models.support           # noqa: F401
import app.models.auth_enhanced     # noqa: F401
import app.models.hse               # noqa: F401
import app.models.tasks             # noqa: F401
import app.models.contracts         # noqa: F401
import app.models.messages          # noqa: F401
import app.models.settings          # noqa: F401
import app.models.workflow          # noqa: F401
import app.models.marketing        # noqa: F401
import app.models.subscription     # noqa: F401
import app.models.report           # noqa: F401
import app.models.reporting        # noqa: F401
import app.models.customer         # noqa: F401
import app.models.order            # noqa: F401
import app.models.pricing          # noqa: F401
import app.models.product          # noqa: F401
import app.models.sales_representative  # noqa: F401
import app.models.sales_reporting  # noqa: F401
import app.models.integration      # noqa: F401
import app.models.mobile           # noqa: F401
import app.models.admin            # noqa: F401
import app.models.ai_core          # noqa: F401
import app.models.analytics        # noqa: F401
import app.models.permission_engine  # noqa: F401
import app.models.payroll_calculator  # noqa: F401
import app.models.bi_tasks         # noqa: F401
import app.models.quality          # noqa: F401
import app.models.projects         # noqa: F401
import app.models.budget           # noqa: F401
import app.models.document         # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Return sync DB URL (postgresql:// not postgresql+asyncpg://)."""
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    return url.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline() -> None:
    url = get_url()
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
        url=get_url(),
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
