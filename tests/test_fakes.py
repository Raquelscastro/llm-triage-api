import json

# Uma resposta válida de LLM, usada pelos testes.
VALID_RESPONSE = json.dumps(
    {"category": "praise", "urgency": "low", "summary": "Elogio ao entregador."}
)


class SequenceLLMClient:
    """LLM de teste: devolve uma resposta da lista por chamada e conta as chamadas."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls = 0

    def classify(self, message: str) -> str:
        response = self._responses[self.calls]
        self.calls += 1
        return response


class FailingLLMClient:
    """LLM de teste: sempre levanta o erro informado."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def classify(self, message: str) -> str:
        raise self._error