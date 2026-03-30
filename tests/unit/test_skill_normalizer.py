from app.tools.skill_normalizer import normalize_skill, normalize_skills


def test_normalize_single_skill() -> None:
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill(" fast api ") == "FastAPI"
    assert normalize_skill("python") == "Python"


def test_normalize_skills_deduplicates() -> None:
    skills = ["python", "Python", "postgres", "PostgreSQL", "fast api"]
    normalized = normalize_skills(skills)

    assert normalized == ["Python", "PostgreSQL", "FastAPI"]