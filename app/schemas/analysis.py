from pydantic import BaseModel, Field


class ResumeExtractionResponse(BaseModel):
    resume_source: str = Field(..., description="Whether resume text came from file upload or raw text.")
    resume_filename: str | None = Field(default=None)
    resume_text: str
    resume_char_count: int

    job_description_source: str | None = Field(
        default=None,
        description="Whether job description came from direct text or URL.",
    )
    job_description_text: str | None = None
    job_description_char_count: int | None = None
    job_url: str | None = None