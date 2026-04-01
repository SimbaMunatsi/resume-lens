from app.schemas.analysis import (
    CandidateProfile,
    FinalAnalysisReport,
    GapAnalysisReport,
    ResumeExtractionResponse,
)


def test_full_analysis_flow_with_text_inputs(client, auth_headers, monkeypatch):
    def fake_run_full_analysis(**kwargs):
        response = ResumeExtractionResponse(
            resume_source="text",
            resume_filename=None,
            resume_text="Jane Doe\nPython Developer",
            resume_char_count=25,
            job_description_source="text",
            job_description_text="Backend role with Python and Docker",
            job_description_char_count=35,
            job_url=None,
            candidate_profile=CandidateProfile(
                name="Jane Doe",
                skills=["Python", "FastAPI"],
                projects=["ResumeCopilot"],
                inferred_seniority="mid-level",
            ),
            gap_analysis=GapAnalysisReport(
                match_score=75,
                strong_matches=["Python"],
                missing_skills=["Docker"],
                weak_sections=["projects"],
                ats_keyword_gaps=["Docker"],
                top_recommendations=["Add Docker evidence."],
                scoring_notes="Stable test score.",
            ),
            final_report=FinalAnalysisReport(
                candidate_name="Jane Doe",
                inferred_seniority="mid-level",
                match_score=75,
                summary="Good baseline fit.",
                strengths=["Python"],
                weaknesses=["projects"],
                rewritten_bullets=["Built backend services using FastAPI."],
                ats_keywords=["Docker"],
                role_fit_feedback="Moderate fit.",
                interview_questions=["How would you use Docker in development?"],
                action_plan=["Add Docker to project bullets."],
                scoring_notes="Stable test score.",
            ),
        )
        return response, 123

    monkeypatch.setattr(
        "app.api.v1.endpoints.analysis.run_full_analysis",
        fake_run_full_analysis,
    )

    response = client.post(
        "/api/v1/analysis/run",
        data={
            "resume_text": "Jane Doe\nPython Developer",
            "job_description_text": "Backend role with Python and Docker",
            "rewrite_style": "technical",
            "target_role": "Backend Engineer",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["candidate_profile"]["name"] == "Jane Doe"
    assert data["gap_analysis"]["match_score"] == 75
    assert data["final_report"]["summary"] == "Good baseline fit."


def test_analysis_flow_returns_validation_error(client, auth_headers):
    response = client.post(
        "/api/v1/analysis/run",
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Provide either resume_file or resume_text."