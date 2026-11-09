from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas das variáveis de ambiente (e do arquivo .env)."""

    # env_file: também lê o arquivo .env
    # extra="ignore": ignora variáveis do .env que ainda não declaramos aqui
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Qual fogão usar. O valor padrão "fake" garante que o projeto sempre liga, sem custo.
    llm_provider: Literal["fake", "gemini"] = "fake"

    # SecretStr esconde o valor quando o objeto é impresso (em logs, por exemplo).
    # Para usar o valor de verdade: settings.gemini_api_key.get_secret_value()
    gemini_api_key: SecretStr | None = None

    gemini_model: str = "gemini-flash-latest"

    # Quanto tempo esperar a resposta do LLM antes de desistir. Precisa ser maior que zero.
    llm_timeout_seconds: float = Field(default=20.0, gt=0)