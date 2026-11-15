from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import Settings
from app.database import Base

# Importar o model registra a tabela no Base. Sem isso, o fiscal não vê nada para criar.
from app.models import triage  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# O endereço do banco vem do .env, e nunca de um arquivo que vai para o Git.
config.set_main_option("sqlalchemy.url", Settings().database_url.get_secret_value())

# O "molde" que o fiscal compara com o caderno.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline: só gera o SQL, sem conectar ao banco."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo normal: conecta ao banco e aplica as fichas."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
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