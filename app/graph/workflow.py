from langgraph.graph import END, START, StateGraph

from app.agents.parsing_agent import ParsingAgent
from app.graph.state import ResumeAnalysisState
from app.llm.provider import get_parsing_llm


def build_resume_analysis_graph():
    llm = get_parsing_llm()
    parsing_agent = ParsingAgent(llm=llm)

    def parse_resume_node(state: ResumeAnalysisState) -> dict:
        resume_text = state.get("resume_text", "")
        profile = parsing_agent.parse(resume_text)
        return {"candidate_profile": profile}

    graph_builder = StateGraph(ResumeAnalysisState)
    graph_builder.add_node("parse_resume", parse_resume_node)
    graph_builder.add_edge(START, "parse_resume")
    graph_builder.add_edge("parse_resume", END)

    return graph_builder.compile()