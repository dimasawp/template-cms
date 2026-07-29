import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- CUSTOM: Add project root to sys.path ---
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.config import settings
from app.core.database import Base

# Import all models here for 'autogenerate' support
from app.modules.users.models.user_model import User
from app.modules.users.models.password_reset_model import PasswordReset
from app.modules.roles.models.role_model import Role, Permission
from app.modules.audit.models.audit_model import AuditLog
from app.modules.settings.models.setting_model import Setting
from app.modules.auth.models.session_model import UserSession
from app.modules.media.models.media_model import Media
from app.modules.notifications.models.notification_model import Notification
from app.modules.categories.models.category_model import Category
from app.modules.posts.models.post_model import Post
# ---------------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Overwrite sqlalchemy.url with the one from our settings
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True # Important for SQLite, harmless for others
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
