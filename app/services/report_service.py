from app.schemas.analysis import CandidateProfile, FinalAnalysisReport, GapAnalysisReport, ImprovementReport


def build_final_report(
    candidate_profile: CandidateProfile,
    gap_analysis: GapAnalysisReport,
    improvement_report: ImprovementReport,
) -> FinalAnalysisReport:
    return FinalAnalysisReport(
        candidate_name=candidate_profile.name,
        inferred_seniority=candidate_profile.inferred_seniority,
        match_score=gap_analysis.match_score,
        summary=improvement_report.summary,
        strengths=improvement_report.strengths or gap_analysis.strong_matches,
        weaknesses=improvement_report.weaknesses or gap_analysis.weak_sections,
        rewritten_bullets=improvement_report.rewritten_bullets,
        ats_keywords=improvement_report.ats_keywords or gap_analysis.ats_keyword_gaps,
        role_fit_feedback=improvement_report.role_fit_feedback,
        interview_questions=improvement_report.interview_questions,
        action_plan=improvement_report.action_plan or gap_analysis.top_recommendations,
        scoring_notes=gap_analysis.scoring_notes,
    )