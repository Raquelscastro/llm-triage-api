from app.llm.errors import LLMAPIError, LLMTimeoutError
from app.llm.fake import FakeLLMClient
from tests.test_fakes import VALID_RESPONSE, FailingLLMClient, SequenceLLMClient


def test_post_triage_returns_classification_and_saves_it(client_factory):
    client = client_factory(FakeLLMClient())

    response = client.post("/triage", json={"message": "Meu pedido atrasou"})

    assert response.status_code == 200
    assert response.json()["category"] == "late_delivery"
    saved = client.get("/triages").json()
    assert len(saved) == 1
    assert saved[0]["message"] == "Meu pedido atrasou"


def test_empty_message_returns_422_and_never_calls_llm(client_factory):
    llm = SequenceLLMClient([VALID_RESPONSE])
    client = client_factory(llm)

    response = client.post("/triage", json={"message": ""})

    assert response.status_code == 422
    assert llm.calls == 0


def test_whitespace_only_message_returns_422(client_factory):
    client = client_factory(FakeLLMClient())

    response = client.post("/triage", json={"message": "     "})

    assert response.status_code == 422


def test_invalid_llm_response_returns_502_and_saves_nothing(client_factory):
    client = client_factory(FakeLLMClient("isto nao e um json"))

    response = client.post("/triage", json={"message": "oi"})

    assert response.status_code == 502
    assert "tentativas" in response.json()["detail"]
    assert client.get("/triages").json() == []


def test_llm_timeout_returns_504(client_factory):
    client = client_factory(FailingLLMClient(LLMTimeoutError("demorou demais")))

    response = client.post("/triage", json={"message": "oi"})

    assert response.status_code == 504
    assert response.json()["detail"] == "demorou demais"


def test_llm_api_error_returns_502(client_factory):
    client = client_factory(FailingLLMClient(LLMAPIError("chave inválida")))

    response = client.post("/triage", json={"message": "oi"})

    assert response.status_code == 502
    assert response.json()["detail"] == "chave inválida"


def test_retry_recovers_from_one_bad_response(client_factory):
    llm = SequenceLLMClient(["lixo", VALID_RESPONSE])
    client = client_factory(llm)

    response = client.post("/triage", json={"message": "oi"})

    assert response.status_code == 200
    assert llm.calls == 2
