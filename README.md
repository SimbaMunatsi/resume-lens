# ResumeCopilot

An AI-powered resume analyzer built with **FastAPI**, **LangGraph**, and **PostgreSQL**.

ResumeCopilot takes a resume plus an optional target job description, then:

- parses the resume into a structured candidate profile
- compares the profile against the target role
- identifies strengths and gaps
- rewrites weak content
- suggests ATS keywords
- generates interview questions
- stores report history and user preferences for future runs

---

## Why this project matters

This project demonstrates practical **agentic AI backend engineering** in a realistic but manageable scope.

It shows:

- multi-step agent orchestration with **LangGraph**
- structured LLM output with **Pydantic**
- external tool integration for resume parsing and job description fetching
- memory design with short-term workflow state and long-term PostgreSQL persistence
- production-style FastAPI architecture
- authentication, history, preferences, logging, and Docker packaging

This is not a toy chatbot. It is a backend system designed to look and behave like a modern AI application.

---

## Core features

- Resume upload support for **PDF**, **DOCX**, and **TXT**
- Direct pasted resume text support
- Optional job description input via:
  - pasted text
  - public job URL
- 3-agent LangGraph workflow:
  - Resume Parsing Agent
  - Gap Analysis Agent
  - Improvement Agent
- Structured candidate profile extraction
- Deterministic job match scoring
- ATS keyword gap detection
- Resume bullet rewriting with style modes:
  - concise
  - technical
  - achievement-focused
- Interview question generation
- Analysis history persistence
- User preference memory
- JWT authentication
- Dockerized local development setup

---

## Architecture

### High-level system diagram

```text
User
  |
  v
FastAPI API Layer
  |
  v
Analysis Service
  |
  v
LangGraph Workflow
  ├── Parse Resume Node
  ├── Gap Analysis Node
  └── Improvement Node
  |
  v
Persistence Layer
  ├── Analysis
  ├── Report
  └── UserPreference
  |
  v
PostgreSQL
```

### Agent workflow diagram

```text
Input
  -> Resume Extraction Tool
  -> Job Description Fetch Tool (optional)
  -> Parse Resume Agent
  -> Gap Analysis Agent
  -> Improvement Agent
  -> Final Report Assembly
  -> Save Analysis + Report + Preferences
```

---

## Agent workflow

### 1. Resume Parsing & Profiling Agent
Converts raw resume text into a structured candidate profile.

Outputs include:
- name
- contact links
- education
- skills
- projects
- certifications
- inferred seniority
- missing sections

### 2. Job Match & Gap Analysis Agent
Compares the candidate profile against the target job description.

Outputs include:
- match score
- strong matches
- missing skills
- weak sections
- ATS keyword gaps
- recommendations

### 3. Resume Improvement Agent
Turns the analysis into actionable improvements.

Outputs include:
- rewritten bullets
- ATS keywords
- role-fit feedback
- interview questions
- action plan

---

## Tools used

### Resume Extraction Tool
Supports:
- PDF via `pypdf`
- DOCX via `python-docx`
- TXT via UTF-8 decoding

### Job Description Fetch Tool
Fetches and parses public HTML job pages using:
- `requests`
- `beautifulsoup4`

### Skill Normalization Tool
Normalizes skill aliases such as:
- `Postgres` -> `PostgreSQL`
- `fast api` -> `FastAPI`
- `js` -> `JavaScript`

---

## Memory design

### Short-term memory
Short-term workflow memory is handled through **LangGraph state** during a single analysis run.

This stores:
- normalized resume text
- normalized job description text
- candidate profile
- gap analysis
- improvement report
- final report

### Long-term memory
Long-term memory is stored in **PostgreSQL** tables.

This stores:
- past analyses
- saved reports
- preferred rewrite style
- preferred target roles
- common skill gaps
- last analysis summary

This allows the system to reuse stored preferences in future runs.

---

## Tech stack

- **FastAPI**
- **LangGraph**
- **LangChain / OpenAI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Pytest**
- **Docker / Docker Compose**

---

## Project structure

```text
app/
├── agents/         # LangGraph agent logic
├── api/            # FastAPI endpoints and dependencies
├── core/           # config, logging, security
├── db/             # database session and metadata base
├── graph/          # workflow state, nodes, and graph assembly
├── llm/            # provider and prompts
├── models/         # SQLAlchemy models
├── repositories/   # database access layer
├── schemas/        # Pydantic request/response models
├── services/       # orchestration and report services
└── tools/          # extraction, fetching, normalization utilities
```

---

## Setup instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd resume-copilot
```

### 2. Create environment file

```bash
cp .env.example .env
```

Update `.env` with your actual values, especially:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run locally

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

App will start at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## Docker usage

### Start app and database

```bash
docker-compose up --build
```

### Stop services

```bash
docker-compose down
```

### Reset containers and volumes

```bash
docker-compose down -v
docker-compose up --build
```

---

## API endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Analysis
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/history`

### Reports
- `GET /api/v1/reports/{analysis_id}`

### Memory
- `GET /api/v1/memory/preferences`
- `PATCH /api/v1/memory/preferences`

### Health
- `GET /api/v1/health`

---

## Sample request

### Register

```json
{
  "username": "simba",
  "email": "simba@example.com",
  "password": "secret123"
}
```

### Run analysis

This endpoint accepts `multipart/form-data`.

Example fields:
- `resume_text`
- `job_description_text`
- `rewrite_style`
- `target_role`

Example values:

```text
resume_text=Jane Doe
Backend Engineer
Skills: Python, FastAPI, PostgreSQL
Projects: ResumeCopilot

job_description_text=Hiring backend engineer with Python, FastAPI, PostgreSQL, Docker.

rewrite_style=technical
target_role=Backend Engineer
```

---

## Sample response

```json
{
  "resume_source": "text",
  "resume_filename": null,
  "resume_text": "Jane Doe\nBackend Engineer\nSkills: Python, FastAPI, PostgreSQL\nProjects: ResumeCopilot",
  "resume_char_count": 88,
  "job_description_source": "text",
  "job_description_text": "Hiring backend engineer with Python, FastAPI, PostgreSQL, Docker.",
  "job_description_char_count": 67,
  "job_url": null,
  "candidate_profile": {
    "name": "Jane Doe",
    "contact_links": [],
    "experience_summary": "Backend-focused engineer with API and database experience.",
    "education": [],
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "projects": ["ResumeCopilot"],
    "certifications": [],
    "inferred_seniority": "mid-level",
    "missing_sections": []
  },
  "gap_analysis": {
    "match_score": 75,
    "strong_matches": ["Python", "FastAPI", "PostgreSQL"],
    "missing_skills": ["Docker"],
    "weak_sections": [],
    "ats_keyword_gaps": ["Docker"],
    "top_recommendations": [
      "Add Docker evidence if applicable.",
      "Strengthen project bullets with clearer impact."
    ],
    "scoring_notes": "Score based on aligned skills and limited gaps."
  },
  "final_report": {
    "candidate_name": "Jane Doe",
    "inferred_seniority": "mid-level",
    "match_score": 75,
    "summary": "Candidate has a solid backend foundation with room to improve keyword alignment.",
    "strengths": ["Python", "FastAPI"],
    "weaknesses": ["Missing Docker evidence"],
    "rewritten_bullets": [
      "Implemented backend services using FastAPI and PostgreSQL with modular application structure.",
      "Designed API functionality with maintainable service boundaries and structured data handling."
    ],
    "ats_keywords": ["Docker", "AWS"],
    "role_fit_feedback": "Moderate fit for the role.",
    "interview_questions": [
      "How would you secure a FastAPI backend in production?",
      "How would you design database migrations safely?"
    ],
    "action_plan": [
      "Add Docker evidence if applicable.",
      "Strengthen project bullets with clearer impact."
    ],
    "scoring_notes": "Score based on aligned skills and limited gaps."
  }
}
```

---

## Testing

Run all tests:

```bash
pytest -q
```

The project includes:
- unit tests for tools and agents
- integration tests for analysis, reports, and auth-protected access

---

## Production hardening included

- structured request logging
- graph node execution logging
- centralized exception handling
- controlled failure handling for job URL fetches
- service/repository separation
- JWT-protected endpoints
- persisted report history
- reusable user preferences

---

## Future improvements

- downloadable PDF report export
- richer job description parsing heuristics
- async background processing
- Redis-backed graph checkpointing
- report comparison across multiple analysis runs
- frontend dashboard
- cloud deployment pipeline
- evaluation suite for parser and report quality

---

## Why this repo is portfolio-worthy

This project demonstrates more than just calling an LLM API.

It shows:
- real backend structure
- agent orchestration
- structured model outputs
- persistence and memory
- production-style packaging
- practical business value

That combination is what makes it a strong portfolio project for AI backend or agentic AI engineering roles.