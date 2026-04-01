from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.analysis import get_analysis_by_id_for_user
from app.repositories.report import get_report_by_analysis_id
from app.schemas.analysis import FinalAnalysisReport, SavedReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{analysis_id}", response_model=SavedReportResponse)
def get_saved_report(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedReportResponse:
    analysis = get_analysis_by_id_for_user(db, analysis_id, current_user.id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    report = get_report_by_analysis_id(db, analysis_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this analysis.",
        )

    return SavedReportResponse(
        analysis_id=analysis_id,
        final_report=FinalAnalysisReport(**report.final_report_json),
        created_at=report.created_at,
    )