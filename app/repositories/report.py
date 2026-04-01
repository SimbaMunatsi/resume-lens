from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report


def create_report(
    db: Session,
    *,
    analysis_id: int,
    match_score: int,
    candidate_profile_json: dict,
    gap_analysis_json: dict,
    final_report_json: dict,
) -> Report:
    report = Report(
        analysis_id=analysis_id,
        match_score=match_score,
        candidate_profile_json=candidate_profile_json,
        gap_analysis_json=gap_analysis_json,
        final_report_json=final_report_json,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report_by_analysis_id(db: Session, analysis_id: int) -> Report | None:
    stmt = select(Report).where(Report.analysis_id == analysis_id)
    return db.scalar(stmt)