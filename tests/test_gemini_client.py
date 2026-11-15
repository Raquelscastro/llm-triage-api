from types import SimpleNamespace

import httpx
import pytest

from app.llm.errors import LLMTimeoutError
from app.llm.gemini import GeminiClient, _friendly_api_message


def make_client(generate_content) -> GeminiClient:
    client = GeminiClient(api_key="fake-key", model="fake-model", timeout_seconds=5)
    # Troca o SDK real por um de mentira: nenhum teste chama a internet.
    client._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    return client


def test_returns_text_from_sdk():
    client = make_client(lambda **kwargs: SimpleNamespace(text='{"ok": true}'))

    assert client.classify("oi") == '{"ok": true}'


def test_empty_text_becomes_empty_string():
    client = make_client(lambda **kwargs: SimpleNamespace(text=None))

    assert client.classify("oi") == ""


def test_timeout_becomes_llm_timeout_error():
    def raise_timeout(**kwargs):
        raise httpx.TimeoutException("demorou")

    client = make_client(raise_timeout)

    with pytest.raises(LLMTimeoutError):
        client.classify("oi")


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (429, "Limite de uso"),
        (401, "GEMINI_API_KEY"),
        (404, "GEMINI_MODEL"),
        (500, "500"),
    ],
)
def test_friendly_api_message(code, expected):
    assert expected in _friendly_api_message(code)