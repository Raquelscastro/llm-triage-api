from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.fake import FakeLLMClient
from app.llm.gemini import GeminiClient
from app.services.triage import TriageService


@lru_cache
def get_settings() -> Settings:
    """Lê o .env uma vez só e guarda na memória."""
    return Settings()


def get_llm_client(settings: Annotated[Settings, Depends(get_settings)]) -> LLMClient:
    """Escolhe qual fogão usar. É o ÚNICO lugar que decide isso."""
    if settings.llm_provider == "gemini":
        if settings.gemini_api_key is None:
            raise RuntimeError("LLM_PROVIDER=gemini, mas a GEMINI_API_KEY não está no .env.")
        return GeminiClient(
            api_key=settings.gemini_api_key.get_secret_value(),
            model=settings.gemini_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    return FakeLLMClient()


def get_triage_service(llm: Annotated[LLMClient, Depends(get_llm_client)]) -> TriageService:
    """Monta a Marta, entregando o fogão que o get_llm_client escolheu."""
    return TriageService(llm)
