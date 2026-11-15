from app.llm.fake import FakeLLMClient


def test_health_returns_ok(client_factory):
    client = client_factory(FakeLLMClient())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}