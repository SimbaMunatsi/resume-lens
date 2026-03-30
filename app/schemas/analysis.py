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


class GapAnalysisReport(BaseModel):
    match_score: int = Field(..., ge=0, le=100)
    strong_matches: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    weak_sections: list[str] = Field(default_factory=list)
    ats_keyword_gaps: list[str] = Field(default_factory=list)
    top_recommendations: list[str] = Field(default_factory=list)
    scoring_notes: str | None = None


class ImprovementReport(BaseModel):
    rewrite_style: Literal["concise", "technical", "achievement-focused"] = "concise"
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    rewritten_bullets: list[str] = Field(default_factory=list)
    ats_keywords: list[str] = Field(default_factory=list)
    role_fit_feedback: str
    interview_questions: list[str] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)


class FinalAnalysisReport(BaseModel):
    candidate_name: str | None = None
    inferred_seniority: Literal["student", "junior", "mid-level", "senior", "unknown"] = "unknown"
    match_score: int = Field(..., ge=0, le=100)
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    rewritten_bullets: list[str] = Field(default_factory=list)
    ats_keywords: list[str] = Field(default_factory=list)
    role_fit_feedback: str
    interview_questions: list[str] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)
    scoring_notes: str | None = None


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
    gap_analysis: GapAnalysisReport | None = None
    final_report: FinalAnalysisReport | None = None