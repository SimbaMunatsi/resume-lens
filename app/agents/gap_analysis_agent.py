from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.prompts.gap_prompts import GAP_ANALYSIS_SYSTEM_PROMPT
from app.schemas.analysis import CandidateProfile, GapAnalysisReport
from app.tools.skill_normalizer import normalize_skills


class GapAnalysisAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    def analyze(
        self,
        candidate_profile: CandidateProfile,
        job_description_text: str | None,
    ) -> GapAnalysisReport:
        profile_skills = normalize_skills(candidate_profile.skills)

        if not job_description_text:
            weak_sections = self._infer_weak_sections(candidate_profile, None)

            report = GapAnalysisReport(
                match_score=0,
                strong_matches=profile_skills[:6],
                missing_skills=[],
                weak_sections=weak_sections,
                ats_keyword_gaps=[],
                top_recommendations=self._general_recommendations(candidate_profile, weak_sections),
                scoring_notes="No job description provided, so this report contains general resume feedback only.",
            )
            return report

        jd_skills = self._extract_candidate_skill_keywords(job_description_text)
        matched_skills = [skill for skill in profile_skills if skill.lower() in {s.lower() for s in jd_skills}]
        missing_skills = [skill for skill in jd_skills if skill.lower() not in {s.lower() for s in profile_skills}]

        weak_sections = self._infer_weak_sections(candidate_profile, job_description_text)
        ats_keyword_gaps = missing_skills[:8]
        match_score = self._calculate_match_score(
            matched_count=len(matched_skills),
            jd_skill_count=len(jd_skills),
            weak_section_count=len(weak_sections),
        )

        result: GapAnalysisReport = self.llm.invoke(
            [
                SystemMessage(content=GAP_ANALYSIS_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Candidate profile:\n{candidate_profile.model_dump_json(indent=2)}\n\n"
                        f"Job description text:\n{job_description_text}\n\n"
                        f"Matched skills: {matched_skills}\n"
                        f"Missing skills: {missing_skills}\n"
                        f"Weak sections: {weak_sections}\n"
                        f"ATS keyword gaps: {ats_keyword_gaps}\n"
                        f"Required final score: {match_score}\n"
                    )
                ),
            ]
        )

        result.match_score = match_score
        result.strong_matches = self._dedupe_preserve_order(result.strong_matches or matched_skills)
        result.missing_skills = self._dedupe_preserve_order(missing_skills)
        result.weak_sections = self._normalize_weak_sections(result.weak_sections or weak_sections)
        result.ats_keyword_gaps = self._dedupe_preserve_order(ats_keyword_gaps)
        result.top_recommendations = self._dedupe_preserve_order(result.top_recommendations)

        if not result.scoring_notes:
            result.scoring_notes = (
                f"Score based on matched skills ({len(matched_skills)}/{len(jd_skills) if jd_skills else 0}) "
                f"and {len(weak_sections)} weak resume section(s)."
            )

        return result

    def _extract_candidate_skill_keywords(self, job_description_text: str) -> list[str]:
        known_skill_phrases = [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "SQLAlchemy",
            "Docker",
            "Kubernetes",
            "AWS",
            "GCP",
            "Azure",
            "LangChain",
            "LangGraph",
            "RAG",
            "REST APIs",
            "JavaScript",
            "TypeScript",
            "LLMs",
        ]

        found: list[str] = []
        jd_lower = job_description_text.lower()

        for skill in known_skill_phrases:
            variants = {skill.lower()}
            if skill == "REST APIs":
                variants.update({"rest api", "rest apis"})
            if any(variant in jd_lower for variant in variants):
                found.append(skill)

        return normalize_skills(found)

    def _calculate_match_score(
        self,
        matched_count: int,
        jd_skill_count: int,
        weak_section_count: int,
    ) -> int:
        if jd_skill_count == 0:
            base_score = 50
        else:
            base_score = int((matched_count / jd_skill_count) * 100)

        penalty = min(weak_section_count * 5, 20)
        score = max(0, min(100, base_score - penalty))
        return score

    def _infer_weak_sections(
        self,
        candidate_profile: CandidateProfile,
        job_description_text: str | None,
    ) -> list[str]:
        weak_sections: list[str] = []

        if not candidate_profile.projects:
            weak_sections.append("projects")
        if not candidate_profile.experience_summary:
            weak_sections.append("experience_summary")
        if not candidate_profile.skills:
            weak_sections.append("skills")
        if not candidate_profile.education:
            weak_sections.append("education")
        if not candidate_profile.contact_links:
            weak_sections.append("contact_links")

        if job_description_text:
            jd_lower = job_description_text.lower()
            if "certification" in jd_lower and not candidate_profile.certifications:
                weak_sections.append("certifications")

        return self._normalize_weak_sections(weak_sections)

    def _general_recommendations(
        self,
        candidate_profile: CandidateProfile,
        weak_sections: list[str],
    ) -> list[str]:
        recommendations: list[str] = []

        if "projects" in weak_sections:
            recommendations.append("Add at least 1–2 concrete technical projects with clear outcomes.")
        if "experience_summary" in weak_sections:
            recommendations.append("Add a short professional summary tailored to your target role.")
        if "skills" in weak_sections:
            recommendations.append("Add a dedicated skills section with your main technical tools.")
        if "contact_links" in weak_sections:
            recommendations.append("Include relevant links such as GitHub, LinkedIn, or a portfolio.")
        if candidate_profile.skills:
            recommendations.append("Quantify the impact of your strongest technical work where possible.")

        return self._dedupe_preserve_order(recommendations)

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
    def _normalize_weak_sections(items: list[str]) -> list[str]:
        allowed = {
            "projects",
            "experience_summary",
            "skills",
            "education",
            "contact_links",
            "certifications",
        }
        normalized: list[str] = []

        for item in items:
            cleaned = re.sub(r"\s+", "_", item.strip().lower())
            if cleaned in allowed and cleaned not in normalized:
                normalized.append(cleaned)

        return normalized