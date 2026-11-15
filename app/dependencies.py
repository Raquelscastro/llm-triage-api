from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.fake import FakeLLMClient
from app.llm.gemini import GeminiClient
from app.repositories.triage import TriageRepository
from app.services.triage import TriageService


@lru_cache
def get_settings() -> Settings:
    """Lê o .env uma vez só e guarda na memória."""
    return Settings()


@lru_cache
def get_engine() -> Engine:
    """A ligação com o caderno, criada uma vez só e reaproveitada."""
    settings = get_settings()
    # pool_pre_ping: antes de usar uma conexão guardada, testa se ela ainda está viva.
    return create_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Abre a mesa de trabalho no começo do pedido e fecha no fim, mesmo se der erro."""
    with Session(get_engine()) as session:
        yield session


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


def get_triage_repository(session: Annotated[Session, Depends(get_session)]) -> TriageRepository:
    """Monta a Dona Lúcia, entregando a mesa de trabalho."""
    return TriageRepository(session)


def get_triage_service(
    llm: Annotated[LLMClient, Depends(get_llm_client)],
    repository: Annotated[TriageRepository, Depends(get_triage_repository)],
) -> TriageService:
    """Monta a Marta, entregando o fogão e a arquivista."""
    return TriageService(llm, repository)