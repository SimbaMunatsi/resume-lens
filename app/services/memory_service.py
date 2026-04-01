from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.report import Report
from app.models.user_preference import UserPreference
from app.repositories.analysis import create_analysis
from app.repositories.preferences import get_or_create_user_preferences, update_user_preferences
from app.repositories.report import create_report
from app.schemas.analysis import CandidateProfile, FinalAnalysisReport, GapAnalysisReport


def load_user_preferences(db: Session, user_id: int) -> UserPreference:
    return get_or_create_user_preferences(db, user_id)


def persist_analysis_run(
    db: Session,
    *,
    user_id: int,
    resume_filename: str | None,
    resume_source: str,
    resume_text: str,
    job_description_source: str | None,
    job_description_text: str | None,
    job_url: str | None,
    target_role: str | None,
    rewrite_style: str | None,
    candidate_profile: CandidateProfile,
    gap_analysis: GapAnalysisReport,
    final_report: FinalAnalysisReport,
) -> tuple[Analysis, Report]:
    analysis = create_analysis(
        db,
        user_id=user_id,
        resume_filename=resume_filename,
        resume_source=resume_source,
        resume_text=resume_text,
        job_description_source=job_description_source,
        job_description_text=job_description_text,
        job_url=job_url,
        target_role=target_role,
        rewrite_style=rewrite_style,
    )

    report = create_report(
        db,
        analysis_id=analysis.id,
        match_score=gap_analysis.match_score,
        candidate_profile_json=candidate_profile.model_dump(),
        gap_analysis_json=gap_analysis.model_dump(),
        final_report_json=final_report.model_dump(),
    )

    preference = get_or_create_user_preferences(db, user_id)

    updated_target_roles = list(preference.preferred_target_roles or [])
    if target_role and target_role not in updated_target_roles:
        updated_target_roles.append(target_role)

    update_user_preferences(
        db,
        preference,
        preferred_rewrite_style=rewrite_style,
        preferred_target_roles=updated_target_roles,
        common_skill_gaps=gap_analysis.missing_skills,
        last_analysis_summary={
            "analysis_id": analysis.id,
            "candidate_name": final_report.candidate_name,
            "match_score": final_report.match_score,
            "top_missing_skills": gap_analysis.missing_skills[:5],
        },
    )

    return analysis, report