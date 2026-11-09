from typing import Protocol


class LLMClient(Protocol):
    """Contrato de qualquer cliente de LLM (a "tomada").

    Recebe a mensagem do cliente e devolve o TEXTO bruto da resposta,
    que esperamos ser um JSON. Validar e tentar de novo é papel do service.
    """

    def classify(self, message: str) -> str: ...
