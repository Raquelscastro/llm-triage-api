from fastapi import APIRouter

# Um "grupo de portas". tags só serve para organizar a documentação automática.
router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    # Responde "ok" para quem perguntar se a API está viva.
    return {"status": "ok"}
