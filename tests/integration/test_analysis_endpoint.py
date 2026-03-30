from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_user_and_get_token(email: str, username: str, password: str) -> str:
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


def test_analysis_run_with_raw_text() -> None:
    email, username = unique_identity("analysis_text")
    token = create_user_and_get_token(
        email=email,
        username=username,
        password="secret123",
    )

    response = client.post(
        "/api/v1/analysis/run",
        data={"resume_text": "John Doe\nPython Developer\nFastAPI"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resume_source"] == "text"
    assert "John Doe" in data["resume_text"]


def test_analysis_run_with_raw_text_and_job_description_text() -> None:
    email, username = unique_identity("analysis_jd_text")
    token = create_user_and_get_token(
        email=email,
        username=username,
        password="secret123",
    )

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
    assert "backend engineer" in data["job_description_text"].lower()


def test_analysis_run_rejects_missing_input() -> None:
    email, username = unique_identity("analysis_empty")
    token = create_user_and_get_token(
        email=email,
        username=username,
        password="secret123",
    )

    response = client.post(
        "/api/v1/analysis/run",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Provide either resume_file or resume_text."


def test_analysis_run_with_txt_file() -> None:
    email, username = unique_identity("analysis_file")
    token = create_user_and_get_token(
        email=email,
        username=username,
        password="secret123",
    )

    response = client.post(
        "/api/v1/analysis/run",
        files={"resume_file": ("resume.txt", b"Jane Doe\nML Engineer\nPython", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resume_source"] == "file"
    assert data["resume_filename"] == "resume.txt"
    assert "Jane Doe" in data["resume_text"]


def test_analysis_run_rejects_both_job_inputs() -> None:
    email, username = unique_identity("analysis_both_jd")
    token = create_user_and_get_token(
        email=email,
        username=username,
        password="secret123",
    )

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

def test_analysis_run_returns_gap_analysis() -> None:
    token = create_user_and_get_token(
        email="analysis_gap@example.com",
        username="analysis_gap_user",
        password="secret123",
    )

    response = client.post(
        "/api/v1/analysis/run",
        data={
            "resume_text": "Jane Doe\nBackend Engineer\nSkills: Python, FastAPI, PostgreSQL\nProjects: ResumeCopilot",
            "job_description_text": "Hiring backend engineer with Python, FastAPI, PostgreSQL, Docker.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["candidate_profile"] is not None
    assert data["gap_analysis"] is not None
    assert "match_score" in data["gap_analysis"]    