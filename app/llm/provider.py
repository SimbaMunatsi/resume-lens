from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.schemas.analysis import CandidateProfile, GapAnalysisReport, ImprovementReport


def _base_llm():
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )


def get_parsing_llm():
    return _base_llm().with_structured_output(CandidateProfile, method="json_schema")


def get_gap_analysis_llm():
    return _base_llm().with_structured_output(GapAnalysisReport, method="json_schema")


def get_improvement_llm():
    return _base_llm().with_structured_output(ImprovementReport, method="json_schema")