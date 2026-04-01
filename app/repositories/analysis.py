from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.analysis import Analysis


def create_analysis(
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
) -> Analysis:
    analysis = Analysis(
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
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_history_for_user(db: Session, user_id: int) -> list[Analysis]:
    stmt = (
        select(Analysis)
        .options(selectinload(Analysis.report))
        .where(Analysis.user_id == user_id)
        .order_by(desc(Analysis.created_at))
    )
    return list(db.scalars(stmt).all())


def get_analysis_by_id_for_user(db: Session, analysis_id: int, user_id: int) -> Analysis | None:
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id,
    )
    return db.scalar(stmt)