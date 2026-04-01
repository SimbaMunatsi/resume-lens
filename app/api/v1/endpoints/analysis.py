from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.graph.workflow import build_resume_analysis_graph
from app.models.user import User
from app.repositories.analysis import get_analysis_history_for_user
from app.schemas.analysis import AnalysisHistoryItem, ResumeExtractionResponse
from app.services.memory_service import load_user_preferences, persist_analysis_run
from app.tools.job_fetcher import JobFetchError, fetch_job_description_text
from app.tools.resume_extractor import ResumeExtractionError, extract_resume_text
from app.tools.text_cleaner import clean_text

router = APIRouter(prefix="/analysis", tags=["Analysis"])

resume_analysis_graph = build_resume_analysis_graph()


@router.post(
    "/run",
    response_model=ResumeExtractionResponse,
    status_code=status.HTTP_200_OK,
)
async def run_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    resume_file: UploadFile | None = File(default=None),
    resume_text: str | None = Form(default=None),
    job_description_text: str | None = Form(default=None),
    job_url: str | None = Form(default=None),
    rewrite_style: str | None = Form(default=None),
    target_role: str | None = Form(default=None),
) -> ResumeExtractionResponse:
    if resume_file is None and not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either resume_file or resume_text.",
        )

    if resume_file is not None and resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one of resume_file or resume_text.",
        )

    if job_description_text and job_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one of job_description_text or job_url.",
        )

    preference = load_user_preferences(db, current_user.id)
    effective_rewrite_style = rewrite_style or preference.preferred_rewrite_style or "concise"

    if resume_file is not None:
        file_bytes = await resume_file.read()

        try:
            normalized_resume_text = extract_resume_text(
                filename=resume_file.filename or "uploaded_resume",
                file_bytes=file_bytes,
            )
        except ResumeExtractionError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        resume_source = "file"
        resume_filename = resume_file.filename
    else:
        normalized_resume_text = clean_text(resume_text or "")
        if not normalized_resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided resume_text is empty after cleaning.",
            )

        resume_source = "text"
        resume_filename = None

    normalized_job_description_text: str | None = None
    job_description_source: str | None = None
    normalized_job_url: str | None = None

    if job_description_text:
        normalized_job_description_text = clean_text(job_description_text)
        if not normalized_job_description_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided job_description_text is empty after cleaning.",
            )
        job_description_source = "text"

    elif job_url:
        try:
            normalized_job_description_text = fetch_job_description_text(job_url)
        except JobFetchError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        job_description_source = "url"
        normalized_job_url = job_url

    graph_result = resume_analysis_graph.invoke(
        {
            "user_id": current_user.id,
            "resume_source": resume_source,
            "resume_filename": resume_filename,
            "resume_text": normalized_resume_text,
            "job_description_source": job_description_source,
            "job_description_text": normalized_job_description_text,
            "job_url": normalized_job_url,
            "rewrite_style": effective_rewrite_style,
        }
    )

    persist_analysis_run(
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

    return ResumeExtractionResponse(
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


@router.get("/history", response_model=list[AnalysisHistoryItem])
def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisHistoryItem]:
    analyses = get_analysis_history_for_user(db, current_user.id)

    items: list[AnalysisHistoryItem] = []
    for analysis in analyses:
        match_score = analysis.report.match_score if analysis.report else None
        items.append(
            AnalysisHistoryItem(
                id=analysis.id,
                resume_filename=analysis.resume_filename,
                target_role=analysis.target_role,
                rewrite_style=analysis.rewrite_style,
                match_score=match_score,
                created_at=analysis.created_at,
            )
        )

    return items