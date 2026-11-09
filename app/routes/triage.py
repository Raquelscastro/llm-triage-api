from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_triage_service
from app.schemas.triage import TriageRequest, TriageResult
from app.services.triage import TriageService

router = APIRouter(tags=["triage"])


@router.post("/triage", response_model=TriageResult)
def create_triage(
    payload: TriageRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
) -> TriageResult:
    """Recebe a mensagem, entrega à Marta e devolve o resultado."""
    return service.triage(payload.message)
