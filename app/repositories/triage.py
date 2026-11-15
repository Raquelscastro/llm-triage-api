from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.triage import TriageRecord
from app.schemas.triage import Category, TriageResult, Urgency


class TriageRepository:
    """A arquivista: o único lugar que conversa com o banco."""

    def __init__(self, session: Session) -> None:
        # Recebe a mesa de trabalho pronta, igual a Marta recebe o fogão.
        self._session = session

    def add(self, message: str, result: TriageResult) -> TriageRecord:
        """Anota uma triagem no caderno."""
        record = TriageRecord(
            message=message,
            category=result.category.value,
            urgency=result.urgency.value,
            summary=result.summary,
        )
        self._session.add(record)
        self._session.commit()  # o carimbo: só vale depois dele
        self._session.refresh(record)  # traz o id e a data que o banco gerou
        return record

    def list_triages(
        self,
        category: Category | None = None,
        urgency: Urgency | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TriageRecord]:
        """Consulta o caderno. Cada filtro só entra se for informado."""
        # Mais recentes primeiro. O id desempata quando a data for igual.
        query = select(TriageRecord).order_by(
            TriageRecord.created_at.desc(), TriageRecord.id.desc()
        )
        if category is not None:
            query = query.where(TriageRecord.category == category.value)
        if urgency is not None:
            query = query.where(TriageRecord.urgency == urgency.value)

        query = query.limit(limit).offset(offset)
        return list(self._session.scalars(query))
