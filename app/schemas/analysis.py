from datetime import datetime
from typing import Any, Literal

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


class HistoricalImprovementReport(BaseModel):
    previous_analysis_id: int | None = None
    current_analysis_id: int | None = None
    score_change: int | None = None
    previous_match_score: int | None = None
    current_match_score: int | None = None
    previous_ats_gap_count: int | None = None
    current_ats_gap_count: int | None = None
    improved_areas: list[str] = Field(default_factory=list)
    repeated_weaknesses: list[str] = Field(default_factory=list)
    resolved_weaknesses: list[str] = Field(default_factory=list)
    summary: str | None = None


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
    historical_improvement: HistoricalImprovementReport | None = None


class AnalysisHistoryItem(BaseModel):
    id: int
    resume_filename: str | None = None
    target_role: str | None = None
    rewrite_style: str | None = None
    match_score: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SavedReportResponse(BaseModel):
    analysis_id: int
    final_report: FinalAnalysisReport
    created_at: datetime


class UserPreferenceResponse(BaseModel):
    preferred_rewrite_style: str | None = None
    preferred_target_roles: list[str] = Field(default_factory=list)
    common_skill_gaps: list[str] = Field(default_factory=list)
    last_analysis_summary: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class UserPreferenceUpdateRequest(BaseModel):
    preferred_rewrite_style: Literal["concise", "technical", "achievement-focused"] | None = None
    preferred_target_roles: list[str] | None = None