import logging

from pydantic import ValidationError

from app.llm.base import LLMClient
from app.llm.errors import LLMInvalidResponseError
from app.schemas.triage import TriageResult

logger = logging.getLogger(__name__)


class TriageService:
    """A "cozinha": coordena o cliente LLM, valida a resposta e refaz se vier ruim."""

    def __init__(self, llm_client: LLMClient, max_retries: int = 2) -> None:
        # Recebe o cliente pronto, sem criar um sozinho.
        self._llm = llm_client
        # Quantas vezes REFAZER depois da primeira tentativa.
        self._max_retries = max_retries

    def triage(self, message: str) -> TriageResult:
        total_attempts = self._max_retries + 1

        for attempt in range(1, total_attempts + 1):
            # 1) Pede ao LLM e recebe o TEXTO bruto.
            raw_response = self._llm.classify(message)

            # 2) Prova o prato: se estiver no formato, devolve na hora.
            try:
                return TriageResult.model_validate_json(raw_response)
            except ValidationError:
                # Registramos só o número da tentativa, nunca o conteúdo da mensagem.
                logger.warning(
                    "Resposta inválida do LLM (tentativa %d de %d)", attempt, total_attempts
                )

        # 3) Queimou todas as vezes: avisa com clareza, em vez de servir lixo.
        raise LLMInvalidResponseError(
            f"O LLM devolveu uma resposta fora do formato após {total_attempts} tentativas."
        )