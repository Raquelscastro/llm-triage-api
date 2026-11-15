from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.llm.errors import LLMError, LLMTimeoutError


async def llm_timeout_handler(request: Request, exc: LLMTimeoutError) -> JSONResponse:
    # 504 Gateway Timeout: o serviço de trás demorou demais.
    return JSONResponse(status_code=504, content={"detail": str(exc)})


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    # 502 Bad Gateway: o serviço de trás falhou ou respondeu algo inutilizável.
    return JSONResponse(status_code=502, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    """Cola as regras de tradução na porta do restaurante."""
    # O FastAPI escolhe a regra mais específica: o timeout cai na de 504,
    # e qualquer outro erro de LLM cai na de 502.
    app.add_exception_handler(LLMTimeoutError, llm_timeout_handler)
    app.add_exception_handler(LLMError, llm_error_handler)
