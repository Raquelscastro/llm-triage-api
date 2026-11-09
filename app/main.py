from fastapi import FastAPI

from app.routes import health, triage


def create_app() -> FastAPI:
    """Monta o restaurante: cria o app e registra as portas (rotas)."""
    app = FastAPI(title="API de Triagem de Mensagens", version="0.1.0")
    app.include_router(health.router)
    app.include_router(triage.router)
    return app


# É este objeto que o uvicorn procura para ligar o servidor.
app = create_app()
