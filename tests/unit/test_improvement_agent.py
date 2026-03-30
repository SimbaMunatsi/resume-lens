from app.agents.improvement_agent import ResumeImprovementAgent
from app.schemas.analysis import CandidateProfile, GapAnalysisReport, ImprovementReport


class FakeImprovementLLM:
    def invoke(self, messages):
        prompt_text = ""
        for message in messages:
            content = getattr(message, "content", "")
            if isinstance(content, str):
                prompt_text += content + "\n"

        if "Rewrite style: technical" in prompt_text:
            bullets = [
                "Implemented backend services using FastAPI and PostgreSQL with modular application structure.",
                "Designed API functionality with maintainable service boundaries and structured data handling.",
            ]
        elif "Rewrite style: achievement-focused" in prompt_text:
            bullets = [
                "Built backend services that strengthened application reliability and showcased production-minded engineering skills.",
                "Delivered cleaner API architecture and stronger implementation quality across core backend functionality.",
            ]
        else:
            bullets = [
                "Built backend services using FastAPI and PostgreSQL.",
                "Improved API structure and code organization.",
            ]

        return ImprovementReport(
            rewrite_style="concise",
            summary="Candidate has a solid backend foundation with room to improve keyword alignment.",
            strengths=["Python", "FastAPI"],
            weaknesses=["Missing Docker evidence"],
            rewritten_bullets=bullets,
            ats_keywords=["Docker", "AWS"],
            role_fit_feedback="Moderate fit for the role.",
            interview_questions=[
                "How would you secure a FastAPI backend in production?",
                "How would you design database migrations safely?",
            ],
            action_plan=[
                "Add Docker evidence if applicable.",
                "Strengthen project bullets with clearer impact.",
            ],
        )


def build_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Jane Doe",
        skills=["Python", "FastAPI", "PostgreSQL"],
        projects=["ResumeCopilot"],
        experience_summary="Backend engineer with API experience.",
        education=["BSc Computer Science"],
        contact_links=["https://github.com/janedoe"],
        inferred_seniority="mid-level",
    )


def build_gap_report() -> GapAnalysisReport:
    return GapAnalysisReport(
        match_score=75,
        strong_matches=["Python", "FastAPI", "PostgreSQL"],
        missing_skills=["Docker"],
        weak_sections=["projects"],
        ats_keyword_gaps=["Docker"],
        top_recommendations=[
            "Add Docker experience if you have it.",
            "Strengthen project outcome statements.",
        ],
        scoring_notes="Score based on aligned skills and limited gaps.",
    )


def test_improvement_agent_returns_stable_report() -> None:
    agent = ResumeImprovementAgent(llm=FakeImprovementLLM())

    report = agent.improve(
        candidate_profile=build_profile(),
        gap_analysis=build_gap_report(),
        rewrite_style="concise",
        job_description_text="Backend role with Python, FastAPI, PostgreSQL, Docker.",
    )

    assert report.summary
    assert isinstance(report.strengths, list)
    assert isinstance(report.weaknesses, list)
    assert isinstance(report.rewritten_bullets, list)
    assert isinstance(report.ats_keywords, list)
    assert isinstance(report.interview_questions, list)
    assert isinstance(report.action_plan, list)
    assert report.role_fit_feedback


def test_rewrite_style_changes_output() -> None:
    agent = ResumeImprovementAgent(llm=FakeImprovementLLM())

    concise_report = agent.improve(
        candidate_profile=build_profile(),
        gap_analysis=build_gap_report(),
        rewrite_style="concise",
        job_description_text="Backend role",
    )

    technical_report = agent.improve(
        candidate_profile=build_profile(),
        gap_analysis=build_gap_report(),
        rewrite_style="technical",
        job_description_text="Backend role",
    )

    achievement_report = agent.improve(
        candidate_profile=build_profile(),
        gap_analysis=build_gap_report(),
        rewrite_style="achievement-focused",
        job_description_text="Backend role",
    )

    assert concise_report.rewritten_bullets != technical_report.rewritten_bullets
    assert technical_report.rewritten_bullets != achievement_report.rewritten_bullets
    assert concise_report.rewritten_bullets != achievement_report.rewritten_bullets


def test_invalid_rewrite_style_falls_back_to_concise() -> None:
    agent = ResumeImprovementAgent(llm=FakeImprovementLLM())

    report = agent.improve(
        candidate_profile=build_profile(),
        gap_analysis=build_gap_report(),
        rewrite_style="random-style",
        job_description_text="Backend role",
    )

    assert report.rewrite_style == "concise"