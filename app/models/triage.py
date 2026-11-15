from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TriageRecord(Base):
    """Uma página do caderno: cada linha é uma triagem feita."""

    __tablename__ = "triages"

    # Número da linha, gerado pelo banco. Nunca se repete.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Texto original do cliente. Usamos só dados fictícios neste projeto.
    message: Mapped[str] = mapped_column(Text)

    # index=True cria o "índice remissivo": acelera o filtro do GET /triages.
    # Guardamos como texto. Quem confere os valores é o Pydantic, antes de salvar.
    category: Mapped[str] = mapped_column(String(32), index=True)
    urgency: Mapped[str] = mapped_column(String(16), index=True)

    summary: Mapped[str] = mapped_column(String(200))

    # O próprio banco carimba a data e a hora, com fuso horário.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
