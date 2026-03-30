from typing import TypedDict

from app.schemas.analysis import CandidateProfile, GapAnalysisReport


class ResumeAnalysisState(TypedDict, total=False):
    user_id: int

    resume_source: str
    resume_filename: str | None
    resume_text: str

    job_description_source: str | None
    job_description_text: str | None
    job_url: str | None

    candidate_profile: CandidateProfile
    gap_analysis: GapAnalysisReport

    errors: list[str]