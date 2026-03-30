from __future__ import annotations


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
}


def normalize_skill(skill: str) -> str:
    cleaned = " ".join(skill.strip().split()).lower()
    if not cleaned:
        return ""
    return SKILL_ALIASES.get(cleaned, skill.strip())


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