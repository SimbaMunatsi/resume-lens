from typing import TypedDict

from app.schemas.analysis import CandidateProfile, FinalAnalysisReport, GapAnalysisReport, ImprovementReport


class ResumeAnalysisState(TypedDict, total=False):
    user_id: int

    resume_source: str
    resume_filename: str | None
    resume_text: str

    job_description_source: str | None
    job_description_text: str | None
    job_url: str | None

    rewrite_style: str

    candidate_profile: CandidateProfile
    gap_analysis: GapAnalysisReport
    improvement_report: ImprovementReport
    final_report: FinalAnalysisReport

    errors: list[str]