from types import SimpleNamespace

from app.schemas.analysis import GapAnalysisReport
from app.services.improvement_tracking_service import build_historical_improvement_report


def test_historical_improvement_report_detects_progress() -> None:
    previous_analysis = SimpleNamespace(
        id=10,
        report=SimpleNamespace(
            gap_analysis_json={
                "match_score": 68,
                "ats_keyword_gaps": ["Docker", "AWS", "Kubernetes"],
                "weak_sections": ["projects", "contact_links"],
            }
        ),
    )

    current_gap = GapAnalysisReport(
        match_score=78,
        strong_matches=["Python", "FastAPI"],
        missing_skills=["AWS"],
        weak_sections=["projects"],
        ats_keyword_gaps=["AWS"],
        top_recommendations=["Add AWS evidence."],
        scoring_notes="Improved fit.",
    )

    comparison = build_historical_improvement_report(
        previous_analysis=previous_analysis,
        current_gap_analysis=current_gap,
        current_analysis_id=11,
    )

    assert comparison is not None
    assert comparison.previous_match_score == 68
    assert comparison.current_match_score == 78
    assert comparison.score_change == 10
    assert comparison.previous_ats_gap_count == 3
    assert comparison.current_ats_gap_count == 1
    assert "projects" in comparison.repeated_weaknesses
    assert "contact_links" in comparison.resolved_weaknesses
    assert comparison.summary is not None
    assert "improved from 68 to 78" in comparison.summary.lower()


def test_historical_improvement_report_returns_none_without_previous_analysis() -> None:
    current_gap = GapAnalysisReport(
        match_score=70,
        strong_matches=["Python"],
        missing_skills=["Docker"],
        weak_sections=["projects"],
        ats_keyword_gaps=["Docker"],
        top_recommendations=["Improve project bullets."],
        scoring_notes="Initial run.",
    )

    comparison = build_historical_improvement_report(
        previous_analysis=None,
        current_gap_analysis=current_gap,
        current_analysis_id=1,
    )

    assert comparison is None