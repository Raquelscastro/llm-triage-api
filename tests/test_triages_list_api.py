import pytest
from fastapi.testclient import TestClient

from app.llm.fake import FakeLLMClient
from app.repositories.triage import TriageRepository
from app.schemas.triage import Category, TriageResult, Urgency


@pytest.fixture
def seeded(session):
    """Anota 4 triagens no caderno de teste, da mais antiga para a mais recente."""
    repository = TriageRepository(session)
    rows = [
        ("Atraso grave", Category.LATE_DELIVERY, Urgency.HIGH),
        ("Atraso leve", Category.LATE_DELIVERY, Urgency.LOW),
        ("Cobrado em dobro", Category.BILLING, Urgency.HIGH),
        ("Adorei", Category.PRAISE, Urgency.LOW),
    ]
    for message, category, urgency in rows:
        result = TriageResult(category=category, urgency=urgency, summary="Resumo.")
        repository.add(message, result)


def get_messages(client: TestClient, **params: str | int) -> list[str]:
    response = client.get("/triages", params=params)
    assert response.status_code == 200
    return [row["message"] for row in response.json()]


def test_lists_most_recent_first(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client) == [
        "Adorei",
        "Cobrado em dobro",
        "Atraso leve",
        "Atraso grave",
    ]


def test_filters_by_category(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client, category="late_delivery") == ["Atraso leve", "Atraso grave"]


def test_filters_by_urgency(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client, urgency="high") == ["Cobrado em dobro", "Atraso grave"]


def test_filters_by_category_and_urgency(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client, category="late_delivery", urgency="high") == ["Atraso grave"]


def test_filter_with_no_match_returns_empty_list(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client, category="other") == []


def test_invalid_category_returns_422(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert client.get("/triages", params={"category": "banana"}).status_code == 422


def test_limit_below_minimum_returns_422(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert client.get("/triages", params={"limit": 0}).status_code == 422


def test_limit_above_maximum_returns_422(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert client.get("/triages", params={"limit": 101}).status_code == 422


def test_pagination_with_limit_and_offset(client_factory, seeded):
    client = client_factory(FakeLLMClient())

    assert get_messages(client, limit=2) == ["Adorei", "Cobrado em dobro"]
    assert get_messages(client, limit=2, offset=2) == ["Atraso leve", "Atraso grave"]
