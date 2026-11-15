import logging

from pydantic import ValidationError

from app.llm.base import LLMClient
from app.llm.errors import LLMInvalidResponseError
from app.repositories.triage import TriageRepository
from app.schemas.triage import TriageResult

logger = logging.getLogger(__name__)


class TriageService:
    """A "cozinha": prova o prato, refaz se vier ruim e anota o que foi aprovado."""

    def __init__(
        self,
        llm_client: LLMClient,
        repository: TriageRepository,
        max_retries: int = 2,
    ) -> None:
        # Recebe o fogão e a arquivista prontos, sem criar nenhum dos dois.
        self._llm = llm_client
        self._repository = repository
        # Quantas vezes REFAZER depois da primeira tentativa.
        self._max_retries = max_retries

    def triage(self, message: str) -> TriageResult:
        total_attempts = self._max_retries + 1

        for attempt in range(1, total_attempts + 1):
            # 1) Pede ao LLM e recebe o TEXTO bruto.
            raw_response = self._llm.classify(message)

            # 2) Prova o prato.
            try:
                result = TriageResult.model_validate_json(raw_response)
            except ValidationError:
                # Registramos só o número da tentativa, nunca o conteúdo da mensagem.
                logger.warning(
                    "Resposta inválida do LLM (tentativa %d de %d)", attempt, total_attempts
                )
                continue

            # 3) Prato aprovado: a Dona Lúcia anota no caderno, e só então serve.
            self._repository.add(message, result)
            return result

        # Queimou todas as vezes: nada é anotado, e o aviso é claro.
        raise LLMInvalidResponseError(
            f"O LLM devolveu uma resposta fora do formato após {total_attempts} tentativas."
        )