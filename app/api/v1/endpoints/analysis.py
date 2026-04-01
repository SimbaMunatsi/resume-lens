from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.analysis import get_analysis_history_for_user
from app.schemas.analysis import AnalysisHistoryItem, ResumeExtractionResponse
from app.services.analysis_service import run_full_analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])


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
    file_bytes = await resume_file.read() if resume_file is not None else None

    try:
        response, analysis_id = run_full_analysis(
            db=db,
            current_user=current_user,
            resume_file_name=resume_file.filename if resume_file else None,
            resume_file_bytes=file_bytes,
            resume_text=resume_text,
            job_description_text=job_description_text,
            job_url=job_url,
            rewrite_style=rewrite_style,
            target_role=target_role,
        )
        return response
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


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