from app.models.analysis import Analysis
from app.schemas.analysis import GapAnalysisReport, HistoricalImprovementReport


def build_historical_improvement_report(
    *,
    previous_analysis: Analysis | None,
    current_gap_analysis: GapAnalysisReport,
    current_analysis_id: int | None = None,
) -> HistoricalImprovementReport | None:
    if previous_analysis is None or previous_analysis.report is None:
        return None

    previous_gap_json = previous_analysis.report.gap_analysis_json or {}

    previous_match_score = previous_gap_json.get("match_score")
    previous_ats_gaps = previous_gap_json.get("ats_keyword_gaps", []) or []
    previous_weak_sections = previous_gap_json.get("weak_sections", []) or []

    current_match_score = current_gap_analysis.match_score
    current_ats_gaps = current_gap_analysis.ats_keyword_gaps
    current_weak_sections = current_gap_analysis.weak_sections

    score_change = None
    if isinstance(previous_match_score, int):
        score_change = current_match_score - previous_match_score

    improved_areas: list[str] = []
    repeated_weaknesses = [
        section for section in current_weak_sections if section in previous_weak_sections
    ]
    resolved_weaknesses = [
        section for section in previous_weak_sections if section not in current_weak_sections
    ]

    if isinstance(previous_match_score, int):
        if current_match_score > previous_match_score:
            improved_areas.append(
                f"Match score improved from {previous_match_score} to {current_match_score}."
            )
        elif current_match_score < previous_match_score:
            improved_areas.append(
                f"Match score dropped from {previous_match_score} to {current_match_score}."
            )

    if len(current_ats_gaps) < len(previous_ats_gaps):
        improved_areas.append(
            f"ATS keyword gaps reduced from {len(previous_ats_gaps)} to {len(current_ats_gaps)}."
        )
    elif len(current_ats_gaps) > len(previous_ats_gaps):
        improved_areas.append(
            f"ATS keyword gaps increased from {len(previous_ats_gaps)} to {len(current_ats_gaps)}."
        )

    summary = _build_summary(
        previous_match_score=previous_match_score,
        current_match_score=current_match_score,
        previous_ats_gap_count=len(previous_ats_gaps),
        current_ats_gap_count=len(current_ats_gaps),
        repeated_weaknesses=repeated_weaknesses,
    )

    return HistoricalImprovementReport(
        previous_analysis_id=previous_analysis.id,
        current_analysis_id=current_analysis_id,
        score_change=score_change,
        previous_match_score=previous_match_score if isinstance(previous_match_score, int) else None,
        current_match_score=current_match_score,
        previous_ats_gap_count=len(previous_ats_gaps),
        current_ats_gap_count=len(current_ats_gaps),
        improved_areas=improved_areas,
        repeated_weaknesses=repeated_weaknesses,
        resolved_weaknesses=resolved_weaknesses,
        summary=summary,
    )


def _build_summary(
    *,
    previous_match_score: int | None,
    current_match_score: int,
    previous_ats_gap_count: int,
    current_ats_gap_count: int,
    repeated_weaknesses: list[str],
) -> str:
    parts: list[str] = []

    if previous_match_score is not None:
        if current_match_score > previous_match_score:
            parts.append(f"Match score improved from {previous_match_score} to {current_match_score}.")
        elif current_match_score < previous_match_score:
            parts.append(f"Match score fell from {previous_match_score} to {current_match_score}.")
        else:
            parts.append(f"Match score stayed at {current_match_score}.")

    if current_ats_gap_count < previous_ats_gap_count:
        parts.append(
            f"ATS keyword coverage improved, with gaps reduced from {previous_ats_gap_count} to {current_ats_gap_count}."
        )
    elif current_ats_gap_count > previous_ats_gap_count:
        parts.append(
            f"ATS keyword coverage weakened, with gaps increasing from {previous_ats_gap_count} to {current_ats_gap_count}."
        )
    else:
        parts.append(f"ATS keyword gap count stayed at {current_ats_gap_count}.")

    if repeated_weaknesses:
        pretty = ", ".join(section.replace("_", " ") for section in repeated_weaknesses[:3])
        parts.append(f"Repeated weakness: {pretty}.")

    return " ".join(parts)