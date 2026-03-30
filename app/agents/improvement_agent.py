from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.prompts.improvement_prompts import IMPROVEMENT_SYSTEM_PROMPT
from app.schemas.analysis import CandidateProfile, GapAnalysisReport, ImprovementReport


class ResumeImprovementAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    def improve(
        self,
        candidate_profile: CandidateProfile,
        gap_analysis: GapAnalysisReport,
        rewrite_style: str = "concise",
        job_description_text: str | None = None,
    ) -> ImprovementReport:
        normalized_style = self._normalize_rewrite_style(rewrite_style)

        result: ImprovementReport = self.llm.invoke(
            [
                SystemMessage(content=IMPROVEMENT_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Rewrite style: {normalized_style}\n\n"
                        f"Candidate profile:\n{candidate_profile.model_dump_json(indent=2)}\n\n"
                        f"Gap analysis:\n{gap_analysis.model_dump_json(indent=2)}\n\n"
                        f"Job description text:\n{job_description_text or 'None provided'}\n"
                    )
                ),
            ]
        )

        result.rewrite_style = normalized_style
        result.strengths = self._dedupe_preserve_order(result.strengths)
        result.weaknesses = self._dedupe_preserve_order(result.weaknesses)
        result.rewritten_bullets = self._dedupe_preserve_order(result.rewritten_bullets)
        result.ats_keywords = self._dedupe_preserve_order(result.ats_keywords or gap_analysis.ats_keyword_gaps)
        result.interview_questions = self._dedupe_preserve_order(result.interview_questions)
        result.action_plan = self._dedupe_preserve_order(result.action_plan)

        if not result.summary.strip():
            result.summary = self._fallback_summary(candidate_profile, gap_analysis)

        if not result.role_fit_feedback.strip():
            result.role_fit_feedback = self._fallback_role_fit_feedback(gap_analysis)

        if not result.rewritten_bullets:
            result.rewritten_bullets = self._fallback_rewritten_bullets(
                candidate_profile=candidate_profile,
                rewrite_style=normalized_style,
            )

        if not result.action_plan:
            result.action_plan = self._fallback_action_plan(gap_analysis)

        return result

    @staticmethod
    def _normalize_rewrite_style(rewrite_style: str) -> str:
        allowed = {"concise", "technical", "achievement-focused"}
        cleaned = (rewrite_style or "concise").strip().lower()
        if cleaned not in allowed:
            return "concise"
        return cleaned

    @staticmethod
    def _dedupe_preserve_order(items: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []

        for item in items:
            cleaned = item.strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key not in seen:
                seen.add(key)
                output.append(cleaned)

        return output

    @staticmethod
    def _fallback_summary(
        candidate_profile: CandidateProfile,
        gap_analysis: GapAnalysisReport,
    ) -> str:
        name = candidate_profile.name or "The candidate"
        if gap_analysis.match_score > 0:
            return (
                f"{name} shows relevant alignment for the target role, with strengths in "
                f"{', '.join(gap_analysis.strong_matches[:3]) or 'core technical areas'}."
            )
        return (
            f"{name} has a usable foundation, but the resume would benefit from stronger structure, "
            "clearer positioning, and more concrete project evidence."
        )

    @staticmethod
    def _fallback_role_fit_feedback(gap_analysis: GapAnalysisReport) -> str:
        if gap_analysis.match_score >= 75:
            return "Strong baseline fit, with a few targeted gaps to close."
        if gap_analysis.match_score >= 50:
            return "Moderate fit. The candidate is relevant, but some important keywords or experiences are missing."
        if gap_analysis.match_score > 0:
            return "Partial fit. The profile has some relevant overlap, but significant gaps remain."
        return "General resume guidance only, since no target role was provided."

    def _fallback_rewritten_bullets(
        self,
        candidate_profile: CandidateProfile,
        rewrite_style: str,
    ) -> list[str]:
        if candidate_profile.projects:
            project = candidate_profile.projects[0]
        else:
            project = "technical project"

        if rewrite_style == "technical":
            return [
                f"Engineered {project} using backend-focused tooling and modular service design.",
                f"Implemented API and data-layer functionality with attention to maintainability and structured application flow.",
            ]
        if rewrite_style == "achievement-focused":
            return [
                f"Built {project}, demonstrating practical backend engineering skills across design, implementation, and delivery.",
                f"Strengthened technical project quality through cleaner architecture, clearer structure, and production-minded development practices.",
            ]
        return [
            f"Built {project} using modern backend development practices.",
            "Improved project structure and clarity through modular design and cleaner implementation patterns.",
        ]

    @staticmethod
    def _fallback_action_plan(gap_analysis: GapAnalysisReport) -> list[str]:
        actions: list[str] = []

        for skill in gap_analysis.missing_skills[:3]:
            actions.append(f"Add or strengthen evidence for {skill} if you have real experience with it.")

        for weak_section in gap_analysis.weak_sections[:3]:
            actions.append(f"Improve the {weak_section.replace('_', ' ')} section with clearer, stronger evidence.")

        if not actions:
            actions.append("Refine the strongest bullets to make impact and ownership clearer.")

        return actions