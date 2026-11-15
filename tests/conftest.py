from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_llm_client, get_session
from app.llm.base import LLMClient
from app.main import create_app

# Importar o model registra a tabela no Base.
from app.models import triage as _triage_model  # noqa: F401


@pytest.fixture
def session() -> Iterator[Session]:
    """Banco SQLite em memória, novo a cada teste. Nada de Docker nos testes."""
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session
    engine.dispose()


@pytest.fixture
def client_factory(session: Session) -> Callable[[LLMClient], TestClient]:
    """Cria um cliente HTTP de teste com o LLM de mentira que você escolher."""

    def make(llm_client: LLMClient) -> TestClient:
        app = create_app()
        # Troca as peças reais (Gemini e Postgres) pelas de teste.
        app.dependency_overrides[get_session] = lambda: session
        app.dependency_overrides[get_llm_client] = lambda: llm_client
        return TestClient(app)

    return make
