import json

# Resposta fixa usada por padrão. O json.dumps garante que o texto seja um JSON válido.
# ensure_ascii=False mantém os acentos do português legíveis.
_DEFAULT_RESPONSE = json.dumps(
    {
        "category": "late_delivery",
        "urgency": "medium",
        "summary": "Cliente relata atraso na entrega do pedido.",
    },
    ensure_ascii=False,
)


class FakeLLMClient:
    """Cliente falso: devolve sempre a mesma resposta. Sem rede e sem custo."""

    def __init__(self, response: str = _DEFAULT_RESPONSE) -> None:
        # Permite passar outra resposta, útil para simular um JSON quebrado nos testes.
        self._response = response

    def classify(self, message: str) -> str:
        # Ignora a mensagem de propósito: o Fake não "pensa", só responde.
        return self._response
