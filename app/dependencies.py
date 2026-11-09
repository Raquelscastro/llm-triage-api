from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.fake import FakeLLMClient
from app.services.triage import TriageService


@lru_cache
def get_settings() -> Settings:
    """Lê o .env uma vez só e guarda na memória."""
    return Settings()


def get_llm_client(settings: Annotated[Settings, Depends(get_settings)]) -> LLMClient:
    """Escolhe qual fogão usar. É o ÚNICO lugar que decide isso."""
    if settings.llm_provider == "fake":
        return FakeLLMClient()
    # Na Fase 2, o cliente real entra aqui.
    raise RuntimeError(f"Provedor de LLM não suportado: {settings.llm_provider}")


def get_triage_service(llm: Annotated[LLMClient, Depends(get_llm_client)]) -> TriageService:
    """Monta a Marta, entregando o fogão que o get_llm_client escolheu."""
    return TriageService(llm)
