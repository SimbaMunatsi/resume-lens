from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import ResumeExtractionResponse
from app.tools.resume_extractor import ResumeExtractionError, extract_resume_text
from app.tools.text_cleaner import clean_text

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post(
    "/run",
    response_model=ResumeExtractionResponse,
    status_code=status.HTTP_200_OK,
)
async def run_analysis(
    current_user: User = Depends(get_current_user),
    resume_file: UploadFile | None = File(default=None),
    resume_text: str | None = Form(default=None),
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

    if resume_file is not None:
        file_bytes = await resume_file.read()

        try:
            extracted_text = extract_resume_text(
                filename=resume_file.filename or "uploaded_resume",
                file_bytes=file_bytes,
            )
        except ResumeExtractionError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        return ResumeExtractionResponse(
            source="file",
            filename=resume_file.filename,
            extracted_text=extracted_text,
            extracted_char_count=len(extracted_text),
        )

    cleaned_text = clean_text(resume_text or "")
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided resume_text is empty after cleaning.",
        )

    return ResumeExtractionResponse(
        source="text",
        filename=None,
        extracted_text=cleaned_text,
        extracted_char_count=len(cleaned_text),
    )