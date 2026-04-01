from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.preferences import get_or_create_user_preferences, update_user_preferences
from app.schemas.analysis import UserPreferenceResponse, UserPreferenceUpdateRequest

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/preferences", response_model=UserPreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    preference = get_or_create_user_preferences(db, current_user.id)
    return UserPreferenceResponse.model_validate(preference)


@router.patch("/preferences", response_model=UserPreferenceResponse)
def patch_preferences(
    payload: UserPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    preference = get_or_create_user_preferences(db, current_user.id)

    updated = update_user_preferences(
        db,
        preference,
        preferred_rewrite_style=payload.preferred_rewrite_style,
        preferred_target_roles=payload.preferred_target_roles,
    )
    return UserPreferenceResponse.model_validate(updated)