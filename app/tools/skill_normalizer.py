from __future__ import annotations
from rapidfuzz import fuzz, process


SKILL_ALIASES: dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "sql alchemy": "SQLAlchemy",
    "sqlalchemy": "SQLAlchemy",
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kuberenetes": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "llms": "LLMs",
    "rag": "RAG",
    "lang chain": "LangChain",
    "langchain": "LangChain",
    "lang graph": "LangGraph",
    "langgraph": "LangGraph",
    "team player": "Teamwork",
    "communication skills": "Communication",
    "problem solving skills": "Problem Solving",
    "teaching students": "Teaching",
    "financial reports": "Financial Analysis",
    "brick laying": "Masonry",
    "patient care": "Patient Care",
}


CANONICAL_SKILLS = list(set(SKILL_ALIASES.values())) + [
    # General / Soft Skills
    "Communication",
    "Teamwork",
    "Leadership",
    "Problem Solving",
    "Time Management",
    "Critical Thinking",
    "Adaptability",
    "Customer Service",

    # Business / Admin
    "Project Management",
    "Sales",
    "Marketing",
    "Business Analysis",
    "Operations Management",

    # Finance
    "Accounting",
    "Financial Analysis",
    "Bookkeeping",
    "Budgeting",

    # Healthcare
    "Patient Care",
    "Nursing",
    "Medical Records",
    "Clinical Support",

    # Construction / Trades
    "Construction",
    "Carpentry",
    "Plumbing",
    "Electrical Work",
    "Masonry",

    # Education
    "Teaching",
    "Curriculum Development",
    "Classroom Management",

    # Tech (keep yours)
    "Data Analysis",
    "Software Development",
]

def normalize_skill(skill: str) -> str:
    cleaned = " ".join(skill.strip().split()).lower()

    if not cleaned:
        return ""

    # normalize separators
    cleaned = cleaned.replace("-", " ")
    cleaned = cleaned.replace("_", " ")

    # remove common noise words
    STOPWORDS = ["skills", "skill", "experience", "knowledge"]
    words = [w for w in cleaned.split() if w not in STOPWORDS]
    cleaned = " ".join(words)

    # 1. exact alias match
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]

    # 2. fuzzy match
    match, score, _ = process.extractOne(
        cleaned,
        CANONICAL_SKILLS,
        scorer=fuzz.token_sort_ratio
    )

    if score >= 75:
        return match

    return skill.strip()


def normalize_skills(skills: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized_skill = normalize_skill(skill)
        if not normalized_skill:
            continue

        seen_key = normalized_skill.lower()
        if seen_key not in seen:
            seen.add(seen_key)
            normalized.append(normalized_skill)

    return normalized