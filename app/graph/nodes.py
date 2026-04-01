import logging
import time

from app.agents.gap_analysis_agent import GapAnalysisAgent
from app.agents.improvement_agent import ResumeImprovementAgent
from app.agents.parsing_agent import ParsingAgent
from app.graph.state import ResumeAnalysisState
from app.llm.provider import get_gap_analysis_llm, get_improvement_llm, get_parsing_llm
from app.services.report_service import build_final_report

logger = logging.getLogger("app.graph")

parsing_agent = ParsingAgent(llm=get_parsing_llm())
gap_analysis_agent = GapAnalysisAgent(llm=get_gap_analysis_llm())
improvement_agent = ResumeImprovementAgent(llm=get_improvement_llm())


def parse_resume_node(state: ResumeAnalysisState) -> dict:
    start = time.perf_counter()
    logger.info("graph_node_started node=parse_resume user_id=%s", state.get("user_id"))

    resume_text = state.get("resume_text", "")
    profile = parsing_agent.parse(resume_text)

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "graph_node_completed node=parse_resume user_id=%s latency_ms=%s",
        state.get("user_id"),
        latency_ms,
    )
    return {"candidate_profile": profile}


def gap_analysis_node(state: ResumeAnalysisState) -> dict:
    start = time.perf_counter()
    logger.info("graph_node_started node=gap_analysis user_id=%s", state.get("user_id"))

    candidate_profile = state["candidate_profile"]
    job_description_text = state.get("job_description_text")

    report = gap_analysis_agent.analyze(
        candidate_profile=candidate_profile,
        job_description_text=job_description_text,
    )

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "graph_node_completed node=gap_analysis user_id=%s latency_ms=%s",
        state.get("user_id"),
        latency_ms,
    )
    return {"gap_analysis": report}


def improvement_node(state: ResumeAnalysisState) -> dict:
    start = time.perf_counter()
    logger.info("graph_node_started node=improvement user_id=%s", state.get("user_id"))

    candidate_profile = state["candidate_profile"]
    gap_analysis = state["gap_analysis"]
    job_description_text = state.get("job_description_text")
    rewrite_style = state.get("rewrite_style", "concise")

    improvement_report = improvement_agent.improve(
        candidate_profile=candidate_profile,
        gap_analysis=gap_analysis,
        rewrite_style=rewrite_style,
        job_description_text=job_description_text,
    )

    final_report = build_final_report(
        candidate_profile=candidate_profile,
        gap_analysis=gap_analysis,
        improvement_report=improvement_report,
    )

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "graph_node_completed node=improvement user_id=%s latency_ms=%s",
        state.get("user_id"),
        latency_ms,
    )

    return {
        "improvement_report": improvement_report,
        "final_report": final_report,
    }