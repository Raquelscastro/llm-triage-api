from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Folha-modelo de todas as tabelas. Cada model herda daqui."""