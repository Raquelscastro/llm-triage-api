import pytest
from pydantic import ValidationError

from app.config import Settings

DB_URL = "postgresql+psycopg://user:segredo123@127.0.0.1:5434/db"


def test_database_url_is_hidden_in_repr():
    settings = Settings(_env_file=None, database_url=DB_URL)

    assert "segredo123" not in repr(settings)


def test_unknown_llm_provider_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url=DB_URL, llm_provider="banana")