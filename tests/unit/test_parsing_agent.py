from app.agents.parsing_agent import ParsingAgent
from app.schemas.analysis import CandidateProfile


class FakeStructuredLLM:
    def invoke(self, messages):
        return CandidateProfile(
            name="Simbarashe Munatsi",
            contact_links=[
                "https://github.com/simbarashe",
                "https://github.com/simbarashe",
            ],
            experience_summary="Backend-focused engineer with FastAPI and PostgreSQL experience.",
            education=["BSc Computer Science"],
            skills=["python", "postgres", "fast api", "python"],
            projects=["ResumeCopilot", "Task Manager API", "ResumeCopilot"],
            certifications=["AWS Cloud Practitioner"],
            inferred_seniority="mid-level",
            missing_sections=["summary", "skills", "summary", "invalid-section"],
        )


def test_parsing_agent_returns_predictable_profile() -> None:
    agent = ParsingAgent(llm=FakeStructuredLLM())

    profile = agent.parse("Some resume text here")

    assert profile.name == "Simbarashe Munatsi"
    assert profile.inferred_seniority == "mid-level"
    assert profile.skills == ["Python", "PostgreSQL", "FastAPI"]
    assert profile.contact_links == ["https://github.com/simbarashe"]
    assert profile.projects == ["ResumeCopilot", "Task Manager API"]
    assert profile.missing_sections == ["summary", "skills"]


def test_parsing_agent_output_matches_schema() -> None:
    agent = ParsingAgent(llm=FakeStructuredLLM())
    profile = agent.parse("Resume text")

    assert isinstance(profile, CandidateProfile)
    assert isinstance(profile.education, list)
    assert isinstance(profile.skills, list)
    assert isinstance(profile.projects, list)
    assert isinstance(profile.certifications, list)