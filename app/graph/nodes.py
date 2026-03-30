from app.agents.gap_analysis_agent import GapAnalysisAgent
from app.agents.parsing_agent import ParsingAgent
from app.graph.state import ResumeAnalysisState
from app.llm.provider import get_gap_analysis_llm, get_parsing_llm

parsing_agent = ParsingAgent(llm=get_parsing_llm())
gap_analysis_agent = GapAnalysisAgent(llm=get_gap_analysis_llm())


def parse_resume_node(state: ResumeAnalysisState) -> dict:
    resume_text = state.get("resume_text", "")
    profile = parsing_agent.parse(resume_text)
    return {"candidate_profile": profile}


def gap_analysis_node(state: ResumeAnalysisState) -> dict:
    candidate_profile = state["candidate_profile"]
    job_description_text = state.get("job_description_text")

    report = gap_analysis_agent.analyze(
        candidate_profile=candidate_profile,
        job_description_text=job_description_text,
    )
    return {"gap_analysis": report}