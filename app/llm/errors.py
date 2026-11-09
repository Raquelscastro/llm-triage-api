class LLMError(Exception):
    """Base de todos os erros ao falar com o LLM.

    Ter uma base comum permite pegar "qualquer erro de LLM" com um único except.
    """


class LLMTimeoutError(LLMError):
    """O LLM demorou mais do que o tempo limite."""


class LLMAPIError(LLMError):
    """A API do LLM devolveu erro (chave inválida, limite de uso, instabilidade...)."""