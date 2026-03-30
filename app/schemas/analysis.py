from pydantic import BaseModel, Field


class ResumeExtractionResponse(BaseModel):
    source: str = Field(..., description="Whether text came from file upload or raw text.")
    filename: str | None = Field(default=None)
    extracted_text: str
    extracted_char_count: int