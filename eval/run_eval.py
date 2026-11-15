"""Avalia o modelo: roda as mensagens do dataset e mostra a taxa de acerto por campo.

Uso:
    python -m eval.run_eval          # usa o Gemini do .env (gasta cota gratuita)
    python -m eval.run_eval --fake   # usa o Fake (sem custo): serve de linha de base
"""

import argparse
import json
import time
from pathlib import Path

from pydantic import ValidationError

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.errors import LLMError
from app.llm.fake import FakeLLMClient
from app.llm.gemini import GeminiClient
from app.schemas.triage import TriageResult

DATASET_PATH = Path(__file__).parent / "dataset.json"

Outcome = dict[str, str | None]


def load_samples() -> list[dict[str, str]]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def build_client(use_fake: bool) -> tuple[LLMClient, str]:
    """Devolve o cliente e o nome do modelo, para aparecer no relatório."""
    if use_fake:
        return FakeLLMClient(), "fake (sem IA)"
    settings = Settings()
    if settings.gemini_api_key is None:
        raise SystemExit("GEMINI_API_KEY não encontrada no .env.")
    client = GeminiClient(
        api_key=settings.gemini_api_key.get_secret_value(),
        model=settings.gemini_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    return client, settings.gemini_model


def evaluate(client: LLMClient, samples: list[dict[str, str]], pause: float) -> list[Outcome]:
    """Roda cada mensagem UMA vez, sem retry: queremos medir o modelo puro."""
    outcomes: list[Outcome] = []
    for index, sample in enumerate(samples, start=1):
        outcome: Outcome = {
            "message": sample["message"],
            "expected_category": sample["category"],
            "expected_urgency": sample["urgency"],
            "category": None,
            "urgency": None,
            "error": None,
        }
        try:
            raw = client.classify(sample["message"])
            predicted = TriageResult.model_validate_json(raw)
            outcome["category"] = predicted.category.value
            outcome["urgency"] = predicted.urgency.value
        except ValidationError:
            outcome["error"] = "resposta fora do formato"
        except LLMError as exc:
            outcome["error"] = str(exc)
        outcomes.append(outcome)
        print(f"[{index}/{len(samples)}] processada")
        if pause and index < len(samples):
            time.sleep(pause)  # respeita o limite de uso da camada gratuita
    return outcomes


def percent(part: int, total: int) -> str:
    return f"{part}/{total} ({part / total:.0%})"


def report(outcomes: list[Outcome], model_name: str) -> None:
    total = len(outcomes)
    valid = sum(o["error"] is None for o in outcomes)
    category_hits = sum(o["category"] == o["expected_category"] for o in outcomes)
    urgency_hits = sum(o["urgency"] == o["expected_urgency"] for o in outcomes)

    print(f"\nModelo: {model_name}")
    print(f"Respostas válidas : {percent(valid, total)}")
    print(f"Acerto categoria  : {percent(category_hits, total)}")
    print(f"Acerto urgência   : {percent(urgency_hits, total)}")
    print("(resposta inválida ou com erro conta como erro nos dois campos)")

    mistakes = [
        o
        for o in outcomes
        if o["error"]
        or o["category"] != o["expected_category"]
        or o["urgency"] != o["expected_urgency"]
    ]
    if mistakes:
        print("\nErros:")
        for o in mistakes:
            text = str(o["message"])[:60]
            if o["error"]:
                print(f'- "{text}" -> {o["error"]}')
            else:
                print(
                    f'- "{text}" -> categoria {o["expected_category"]}/{o["category"]}, '
                    f"urgência {o['expected_urgency']}/{o['urgency']} (esperado/obtido)"
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia o classificador de triagem.")
    parser.add_argument("--fake", action="store_true", help="usa o FakeLLMClient (sem custo)")
    parser.add_argument("--pause", type=float, default=5.0, help="segundos entre chamadas")
    args = parser.parse_args()

    client, model_name = build_client(args.fake)
    samples = load_samples()
    pause = 0.0 if args.fake else args.pause
    report(evaluate(client, samples, pause), model_name)


if __name__ == "__main__":
    main()
