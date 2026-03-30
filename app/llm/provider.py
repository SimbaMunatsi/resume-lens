from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.schemas.analysis import CandidateProfile


def get_parsing_llm():
    """
    Returns a chat model configured to emit CandidateProfile directly
    via structured output.
    """
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )
    return llm.with_structured_output(CandidateProfile)