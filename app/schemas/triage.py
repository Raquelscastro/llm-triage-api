from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    LATE_DELIVERY = "late_delivery"
    BILLING = "billing"
    WRONG_ITEM = "wrong_item"
    PRAISE = "praise"
    OTHER = "other"


class Urgency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TriageRequest(BaseModel):
    """Body of POST /triage: what the user sends."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000)


class TriageResult(BaseModel):
    """What the LLM must return (and what the API responds with)."""

    category: Category
    urgency: Urgency
    summary: str = Field(max_length=200)