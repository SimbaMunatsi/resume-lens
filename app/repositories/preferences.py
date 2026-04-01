from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference


def get_or_create_user_preferences(db: Session, user_id: int) -> UserPreference:
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    preference = db.scalar(stmt)

    if preference is None:
        preference = UserPreference(
            user_id=user_id,
            preferred_target_roles=[],
            common_skill_gaps=[],
            last_analysis_summary=None,
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)

    return preference


def update_user_preferences(
    db: Session,
    preference: UserPreference,
    *,
    preferred_rewrite_style: str | None = None,
    preferred_target_roles: list[str] | None = None,
    common_skill_gaps: list[str] | None = None,
    last_analysis_summary: dict | None = None,
) -> UserPreference:
    if preferred_rewrite_style is not None:
        preference.preferred_rewrite_style = preferred_rewrite_style
    if preferred_target_roles is not None:
        preference.preferred_target_roles = preferred_target_roles
    if common_skill_gaps is not None:
        preference.common_skill_gaps = common_skill_gaps
    if last_analysis_summary is not None:
        preference.last_analysis_summary = last_analysis_summary

    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference