from app.agents.gap_analysis_agent import GapAnalysisAgent
from app.schemas.analysis import CandidateProfile, GapAnalysisReport


class FakeGapLLM:
    def invoke(self, messages):
        return GapAnalysisReport(
            match_score=75,
            strong_matches=["Python", "FastAPI"],
            missing_skills=["Docker"],
            weak_sections=["projects"],
            ats_keyword_gaps=["Docker"],
            top_recommendations=[
                "Add Docker to your experience if applicable.",
                "Strengthen project impact statements.",
            ],
            scoring_notes="Placeholder notes from fake model.",
        )


def test_gap_analysis_with_job_description() -> None:
    agent = GapAnalysisAgent(llm=FakeGapLLM())

    profile = CandidateProfile(
        name="Jane Doe",
        skills=["Python", "FastAPI", "PostgreSQL"],
        projects=["ResumeCopilot"],
        experience_summary="Backend engineer with API development experience.",
        education=["BSc Computer Science"],
        contact_links=["https://github.com/janedoe"],
    )

    job_description = "We need a backend engineer with Python, FastAPI, PostgreSQL, and Docker."

    report = agent.analyze(profile, job_description)

    assert report.match_score == 75
    assert "Docker" in report.missing_skills
    assert "Python" in report.strong_matches
    assert report.ats_keyword_gaps == ["Docker"]
    assert isinstance(report.top_recommendations, list)


def test_gap_analysis_without_job_description() -> None:
    agent = GapAnalysisAgent(llm=FakeGapLLM())

    profile = CandidateProfile(
        name="John Doe",
        skills=["Python"],
        projects=[],
        experience_summary=None,
        education=[],
        contact_links=[],
    )

    report = agent.analyze(profile, None)

    assert report.match_score == 0
    assert report.missing_skills == []
    assert "projects" in report.weak_sections
    assert report.scoring_notes is not None
    assert "general resume feedback" in report.scoring_notes.lower()


def test_gap_analysis_report_shape_is_stable() -> None:
    agent = GapAnalysisAgent(llm=FakeGapLLM())

    profile = CandidateProfile(
        name="Sam",
        skills=["Python", "FastAPI"],
        projects=["Task Manager API"],
        experience_summary="Backend developer.",
        education=["BSc"],
        contact_links=["https://linkedin.com/in/sam"],
    )

    report = agent.analyze(profile, "Python FastAPI Docker AWS role")

    assert isinstance(report, GapAnalysisReport)
    assert isinstance(report.strong_matches, list)
    assert isinstance(report.missing_skills, list)
    assert isinstance(report.weak_sections, list)
    assert isinstance(report.ats_keyword_gaps, list)
    assert isinstance(report.top_recommendations, list)
    assert 0 <= report.match_score <= 100