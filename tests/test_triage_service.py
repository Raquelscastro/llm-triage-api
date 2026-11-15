import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.llm.errors import LLMInvalidResponseError
from app.models.triage import TriageRecord
from app.repositories.triage import TriageRepository
from app.schemas.triage import Category, Urgency
from app.services.triage import TriageService
from tests.test_fakes import VALID_RESPONSE, SequenceLLMClient


def count_records(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(TriageRecord)) or 0


def make_service(llm: SequenceLLMClient, session: Session) -> TriageService:
    return TriageService(llm, TriageRepository(session))


def test_valid_response_is_returned_and_saved(session):
    llm = SequenceLLMClient([VALID_RESPONSE])

    result = make_service(llm, session).triage("Adorei o entregador")

    assert result.category == Category.PRAISE
    assert result.urgency == Urgency.LOW
    assert llm.calls == 1
    assert count_records(session) == 1


def test_retries_invalid_response_and_then_succeeds(session):
    llm = SequenceLLMClient(["lixo", "{}", VALID_RESPONSE])

    result = make_service(llm, session).triage("oi")

    assert result.category == Category.PRAISE
    assert llm.calls == 3
    assert count_records(session) == 1


def test_raises_after_all_attempts_fail_and_saves_nothing(session):
    llm = SequenceLLMClient(["lixo", "lixo", "lixo"])

    with pytest.raises(LLMInvalidResponseError):
        make_service(llm, session).triage("oi")

    assert llm.calls == 3
    assert count_records(session) == 0
