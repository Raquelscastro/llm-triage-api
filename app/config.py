from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (e do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: Literal["fake"] = "fake"
