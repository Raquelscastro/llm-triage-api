from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_triage_repository, get_triage_service
from app.models.triage import TriageRecord
from app.repositories.triage import TriageRepository
from app.schemas.triage import Category, TriageRead, TriageRequest, TriageResult, Urgency
from app.services.triage import TriageService

router = APIRouter(tags=["triage"])


@router.post("/triage", response_model=TriageResult)
def create_triage(
    payload: TriageRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
) -> TriageResult:
    """Recebe a mensagem, entrega à Marta e devolve o resultado."""
    return service.triage(payload.message)


@router.get("/triages", response_model=list[TriageRead])
def list_triages(
    repository: Annotated[TriageRepository, Depends(get_triage_repository)],
    category: Category | None = None,
    urgency: Urgency | None = None,
    # Entre 1 e 100 por vez: ninguém pede o caderno inteiro de uma só vez.
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TriageRecord]:
    """Consulta o caderno, com filtros opcionais por categoria e urgência."""
    return repository.list_triages(
        category=category, urgency=urgency, limit=limit, offset=offset
    )