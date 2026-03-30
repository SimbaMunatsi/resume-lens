from langgraph.graph import END, START, StateGraph

from app.graph.nodes import gap_analysis_node, parse_resume_node
from app.graph.state import ResumeAnalysisState


def build_resume_analysis_graph():
    graph_builder = StateGraph(ResumeAnalysisState)

    graph_builder.add_node("parse_resume", parse_resume_node)
    graph_builder.add_node("gap_analysis", gap_analysis_node)

    graph_builder.add_edge(START, "parse_resume")
    graph_builder.add_edge("parse_resume", "gap_analysis")
    graph_builder.add_edge("gap_analysis", END)

    return graph_builder.compile()