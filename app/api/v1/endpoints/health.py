from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/protected-health")
def protected_health_check(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return {
        "status": "ok",
        "message": f"Authenticated as {current_user.email}",
    }