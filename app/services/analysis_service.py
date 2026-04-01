import logging
import time
from typing import Any

from sqlalchemy.orm import Session

from app.graph.workflow import build_resume_analysis_graph
from app.models.user import User
from app.schemas.analysis import ResumeExtractionResponse
from app.services.memory_service import load_user_preferences, persist_analysis_run
from app.tools.job_fetcher import fetch_job_description_text
from app.tools.resume_extractor import extract_resume_text
from app.tools.text_cleaner import clean_text

logger = logging.getLogger("app.analysis")

_resume_analysis_graph = build_resume_analysis_graph()


def _normalize_resume_input(
    *,
    resume_file_name: str | None,
    resume_file_bytes: bytes | None,
    resume_text: str | None,
) -> tuple[str, str, str | None]:
    if resume_file_bytes is None and not resume_text:
        raise ValueError("Provide either resume_file or resume_text.")

    if resume_file_bytes is not None and resume_text:
        raise ValueError("Provide only one of resume_file or resume_text.")

    if resume_file_bytes is not None:
        normalized_resume_text = extract_resume_text(
            filename=resume_file_name or "uploaded_resume",
            file_bytes=resume_file_bytes,
        )
        return "file", normalized_resume_text, resume_file_name

    normalized_resume_text = clean_text(resume_text or "")
    if not normalized_resume_text:
        raise ValueError("Provided resume_text is empty after cleaning.")

    return "text", normalized_resume_text, None


def _normalize_job_input(
    *,
    job_description_text: str | None,
    job_url: str | None,
) -> tuple[str | None, str | None, str | None]:
    if job_description_text and job_url:
        raise ValueError("Provide only one of job_description_text or job_url.")

    if job_description_text:
        normalized_job_description_text = clean_text(job_description_text)
        if not normalized_job_description_text:
            raise ValueError("Provided job_description_text is empty after cleaning.")
        return "text", normalized_job_description_text, None

    if job_url:
        normalized_job_description_text = fetch_job_description_text(job_url)
        return "url", normalized_job_description_text, job_url

    return None, None, None


def run_full_analysis(
    *,
    db: Session,
    current_user: User,
    resume_file_name: str | None,
    resume_file_bytes: bytes | None,
    resume_text: str | None,
    job_description_text: str | None,
    job_url: str | None,
    rewrite_style: str | None,
    target_role: str | None,
) -> tuple[ResumeExtractionResponse, int]:
    preference = load_user_preferences(db, current_user.id)
    effective_rewrite_style = rewrite_style or preference.preferred_rewrite_style or "concise"

    resume_source, normalized_resume_text, resume_filename = _normalize_resume_input(
        resume_file_name=resume_file_name,
        resume_file_bytes=resume_file_bytes,
        resume_text=resume_text,
    )

    job_description_source, normalized_job_description_text, normalized_job_url = _normalize_job_input(
        job_description_text=job_description_text,
        job_url=job_url,
    )

    graph_input: dict[str, Any] = {
        "user_id": current_user.id,
        "resume_source": resume_source,
        "resume_filename": resume_filename,
        "resume_text": normalized_resume_text,
        "job_description_source": job_description_source,
        "job_description_text": normalized_job_description_text,
        "job_url": normalized_job_url,
        "rewrite_style": effective_rewrite_style,
    }

    logger.info(
        "analysis_graph_started user_id=%s rewrite_style=%s target_role=%s",
        current_user.id,
        effective_rewrite_style,
        target_role,
    )
    started = time.perf_counter()

    graph_result = _resume_analysis_graph.invoke(graph_input)

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "analysis_graph_completed user_id=%s latency_ms=%s",
        current_user.id,
        latency_ms,
    )

    analysis, _report = persist_analysis_run(
        db,
        user_id=current_user.id,
        resume_filename=resume_filename,
        resume_source=resume_source,
        resume_text=normalized_resume_text,
        job_description_source=job_description_source,
        job_description_text=normalized_job_description_text,
        job_url=normalized_job_url,
        target_role=target_role,
        rewrite_style=effective_rewrite_style,
        candidate_profile=graph_result["candidate_profile"],
        gap_analysis=graph_result["gap_analysis"],
        final_report=graph_result["final_report"],
    )

    logger.info(
        "analysis_persisted user_id=%s analysis_id=%s match_score=%s",
        current_user.id,
        analysis.id,
        graph_result["gap_analysis"].match_score,
    )

    response = ResumeExtractionResponse(
        resume_source=resume_source,
        resume_filename=resume_filename,
        resume_text=normalized_resume_text,
        resume_char_count=len(normalized_resume_text),
        job_description_source=job_description_source,
        job_description_text=normalized_job_description_text,
        job_description_char_count=(
            len(normalized_job_description_text)
            if normalized_job_description_text is not None
            else None
        ),
        job_url=normalized_job_url,
        candidate_profile=graph_result["candidate_profile"],
        gap_analysis=graph_result["gap_analysis"],
        final_report=graph_result["final_report"],
    )

    return response, analysis.id