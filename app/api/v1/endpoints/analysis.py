from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.graph.workflow import build_resume_analysis_graph
from app.models.user import User
from app.schemas.analysis import ResumeExtractionResponse
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
    resume_file: UploadFile | None = File(default=None),
    resume_text: str | None = Form(default=None),
    job_description_text: str | None = Form(default=None),
    job_url: str | None = Form(default=None),
    rewrite_style: str = Form(default="concise"),
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
            "rewrite_style": rewrite_style,
        }
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