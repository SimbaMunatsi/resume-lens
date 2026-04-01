from uuid import uuid4

from app.schemas.analysis import (
    CandidateProfile,
    FinalAnalysisReport,
    GapAnalysisReport,
    ResumeExtractionResponse,
)


def create_user_and_get_token(client, email: str, username: str, password: str) -> str:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200, login_response.text

    return login_response.json()["access_token"]


def unique_identity(prefix: str) -> tuple[str, str]:
    suffix = uuid4().hex[:8]
    return f"{prefix}_{suffix}@example.com", f"{prefix}_{suffix}"


def fake_run_full_analysis_for_text(**kwargs):
    return (
        ResumeExtractionResponse(
            resume_source="text",
            resume_filename=None,
            resume_text="John Doe\nPython Developer\nFastAPI",
            resume_char_count=len("John Doe\nPython Developer\nFastAPI"),
            job_description_source=(
                "text" if kwargs.get("job_description_text") else None
            ),
            job_description_text=kwargs.get("job_description_text"),
            job_description_char_count=(
                len(kwargs["job_description_text"])
                if kwargs.get("job_description_text")
                else None
            ),
            job_url=kwargs.get("job_url"),
            candidate_profile=CandidateProfile(
                name="John Doe",
                skills=["Python", "FastAPI"],
                projects=["ResumeCopilot"],
                inferred_seniority="mid-level",
            ),
            gap_analysis=GapAnalysisReport(
                match_score=75,
                strong_matches=["Python", "FastAPI"],
                missing_skills=["Docker"] if kwargs.get("job_description_text") else [],
                weak_sections=[],
                ats_keyword_gaps=["Docker"] if kwargs.get("job_description_text") else [],
                top_recommendations=["Add Docker evidence."],
                scoring_notes="Mocked analysis score.",
            ),
            final_report=FinalAnalysisReport(
                candidate_name="John Doe",
                inferred_seniority="mid-level",
                match_score=75,
                summary="Strong baseline fit.",
                strengths=["Python", "FastAPI"],
                weaknesses=["Docker"] if kwargs.get("job_description_text") else [],
                rewritten_bullets=["Built backend APIs with FastAPI."],
                ats_keywords=["Docker"] if kwargs.get("job_description_text") else [],
                role_fit_feedback="Good fit.",
                interview_questions=["How would you containerize this app?"],
                action_plan=["Add Docker experience if applicable."],
                scoring_notes="Mocked analysis score.",
            ),
        ),
        1,
    )


def fake_run_full_analysis_for_file(**kwargs):
    return (
        ResumeExtractionResponse(
            resume_source="file",
            resume_filename="resume.txt",
            resume_text="Jane Doe\nML Engineer\nPython",
            resume_char_count=len("Jane Doe\nML Engineer\nPython"),
            job_description_source=None,
            job_description_text=None,
            job_description_char_count=None,
            job_url=None,
            candidate_profile=CandidateProfile(
                name="Jane Doe",
                skills=["Python", "ML"],
                projects=["ResumeCopilot"],
                inferred_seniority="mid-level",
            ),
            gap_analysis=GapAnalysisReport(
                match_score=70,
                strong_matches=["Python"],
                missing_skills=[],
                weak_sections=[],
                ats_keyword_gaps=[],
                top_recommendations=["Quantify ML project impact."],
                scoring_notes="Mocked file analysis.",
            ),
            final_report=FinalAnalysisReport(
                candidate_name="Jane Doe",
                inferred_seniority="mid-level",
                match_score=70,
                summary="Good technical base.",
                strengths=["Python"],
                weaknesses=[],
                rewritten_bullets=["Built ML-oriented backend workflows."],
                ats_keywords=[],
                role_fit_feedback="Solid baseline.",
                interview_questions=["How do you evaluate ML systems?"],
                action_plan=["Add measurable project outcomes."],
                scoring_notes="Mocked file analysis.",
            ),
        ),
        2,
    )


def test_analysis_run_with_raw_text(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.endpoints.analysis.run_full_analysis",
        fake_run_full_analysis_for_text,
    )

    email, username = unique_identity("analysis_text")
    token = create_user_and_get_token(client, email, username, "secret123")

    response = client.post(
        "/api/v1/analysis/run",
        data={"resume_text": "John Doe\nPython Developer\nFastAPI"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resume_source"] == "text"
    assert "John Doe" in data["resume_text"]


def test_analysis_run_with_raw_text_and_job_description_text(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.endpoints.analysis.run_full_analysis",
        fake_run_full_analysis_for_text,
    )

    email, username = unique_identity("analysis_jd_text")
    token = create_user_and_get_token(client, email, username, "secret123")

    response = client.post(
        "/api/v1/analysis/run",
        data={
            "resume_text": "Jane Doe\nBackend Engineer\nFastAPI, PostgreSQL",
            "job_description_text": "We are hiring a backend engineer with FastAPI and Docker experience.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resume_source"] == "text"
    assert data["job_description_source"] == "text"
    assert "docker" in data["job_description_text"].lower()


def test_analysis_run_rejects_missing_input(client) -> None:
    email, username = unique_identity("analysis_empty")
    token = create_user_and_get_token(client, email, username, "secret123")

    response = client.post(
        "/api/v1/analysis/run",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Provide either resume_file or resume_text."


def test_analysis_run_with_txt_file(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.endpoints.analysis.run_full_analysis",
        fake_run_full_analysis_for_file,
    )

    email, username = unique_identity("analysis_file")
    token = create_user_and_get_token(client, email, username, "secret123")

    response = client.post(
        "/api/v1/analysis/run",
        files={
            "resume_file": (
                "resume.txt",
                b"Jane Doe\nML Engineer\nPython",
                "text/plain",
            )
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resume_source"] == "file"
    assert data["resume_filename"] == "resume.txt"
    assert "Jane Doe" in data["resume_text"]


def test_analysis_run_rejects_both_job_inputs(client) -> None:
    email, username = unique_identity("analysis_both_jd")
    token = create_user_and_get_token(client, email, username, "secret123")

    response = client.post(
        "/api/v1/analysis/run",
        data={
            "resume_text": "John Doe\nEngineer",
            "job_description_text": "Need Python",
            "job_url": "https://example.com/job",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Provide only one of job_description_text or job_url."