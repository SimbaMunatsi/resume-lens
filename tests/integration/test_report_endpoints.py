from app.models.analysis import Analysis
from app.models.report import Report
from app.schemas.analysis import FinalAnalysisReport


def seed_analysis_and_report(db_session, fake_user):
    analysis = Analysis(
        user_id=fake_user.id,
        resume_filename="resume.txt",
        resume_source="text",
        resume_text="Jane Doe\nPython",
        job_description_source="text",
        job_description_text="Python backend role",
        job_url=None,
        target_role="Backend Engineer",
        rewrite_style="technical",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    final_report = FinalAnalysisReport(
        candidate_name="Jane Doe",
        inferred_seniority="mid-level",
        match_score=80,
        summary="Strong fit.",
        strengths=["Python", "FastAPI"],
        weaknesses=["Docker"],
        rewritten_bullets=["Built backend APIs with FastAPI."],
        ats_keywords=["Docker"],
        role_fit_feedback="Strong fit with one gap.",
        interview_questions=["How would you containerize this app?"],
        action_plan=["Add Docker evidence."],
        scoring_notes="Test report.",
    )

    report = Report(
        analysis_id=analysis.id,
        match_score=80,
        candidate_profile_json={"name": "Jane Doe", "skills": ["Python", "FastAPI"]},
        gap_analysis_json={"match_score": 80, "missing_skills": ["Docker"]},
        final_report_json=final_report.model_dump(),
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    return analysis, report


def test_get_analysis_history(client, db_session, fake_user, auth_headers):
    seed_analysis_and_report(db_session, fake_user)

    response = client.get("/api/v1/analysis/history", headers=auth_headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 1
    assert data[0]["match_score"] == 80
    assert data[0]["target_role"] == "Backend Engineer"


def test_get_saved_report(client, db_session, fake_user, auth_headers):
    analysis, _ = seed_analysis_and_report(db_session, fake_user)

    response = client.get(f"/api/v1/reports/{analysis.id}", headers=auth_headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["analysis_id"] == analysis.id
    assert data["final_report"]["match_score"] == 80
    assert data["final_report"]["candidate_name"] == "Jane Doe"