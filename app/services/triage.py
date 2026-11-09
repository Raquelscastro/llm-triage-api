from app.llm.base import LLMClient
from app.schemas.triage import TriageResult


class TriageService:
    """A "cozinha": coordena o cliente LLM e a validação da resposta."""

    def __init__(self, llm_client: LLMClient) -> None:
        # Recebe o cliente pronto, sem criar um sozinho.
        # Assim o service funciona com qualquer cliente que siga o contrato.
        self._llm = llm_client

    def triage(self, message: str) -> TriageResult:
        # 1) Pede ao LLM a classificação e recebe o TEXTO bruto da resposta.
        raw_response = self._llm.classify(message)

        # 2) Valida o texto com o schema. Se estiver fora do formato,
        #    o Pydantic levanta um ValidationError.
        #    (A tentativa de novo e as mensagens de erro entram na Fase 2.)
        return TriageResult.model_validate_json(raw_response)
