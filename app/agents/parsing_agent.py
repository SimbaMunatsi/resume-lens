from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.prompts.parsing_prompts import PARSING_SYSTEM_PROMPT
from app.schemas.analysis import CandidateProfile
from app.tools.skill_normalizer import normalize_skills


class ParsingAgent:
    def __init__(self, llm) -> None:
        self.llm = llm

    def parse(self, resume_text: str) -> CandidateProfile:
        result: CandidateProfile = self.llm.invoke(
            [
                SystemMessage(content=PARSING_SYSTEM_PROMPT),
                HumanMessage(content=f"Resume text:\n\n{resume_text}"),
            ]
        )

        result.skills = normalize_skills(result.skills)
        result.contact_links = self._dedupe_preserve_order(result.contact_links)
        result.education = self._dedupe_preserve_order(result.education)
        result.projects = self._dedupe_preserve_order(result.projects)
        result.certifications = self._dedupe_preserve_order(result.certifications)
        result.missing_sections = self._normalize_missing_sections(result.missing_sections)

        return result

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
    def _normalize_missing_sections(items: list[str]) -> list[str]:
        allowed = {
            "summary",
            "education",
            "projects",
            "certifications",
            "skills",
            "contact_links",
        }
        normalized: list[str] = []

        for item in items:
            cleaned = item.strip().lower()
            if cleaned in allowed and cleaned not in normalized:
                normalized.append(cleaned)

        return normalized