from typing import Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str | None = None
    contact_links: list[str] = Field(default_factory=list)
    experience_summary: str | None = None
    education: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    inferred_seniority: Literal["student", "junior", "mid-level", "senior", "unknown"] = "unknown"
    missing_sections: list[str] = Field(default_factory=list)


class ResumeExtractionResponse(BaseModel):
    resume_source: str
    resume_filename: str | None = None
    resume_text: str
    resume_char_count: int

    job_description_source: str | None = None
    job_description_text: str | None = None
    job_description_char_count: int | None = None
    job_url: str | None = None

    candidate_profile: CandidateProfile | None = None