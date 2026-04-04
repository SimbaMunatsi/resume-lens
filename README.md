# ResumeLens
AI-powered resume analysis and improvement platform built with **FastAPI**, **LangGraph**, **Streamlit**, and **PostgreSQL**.

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![LangGraph](https://img.shields.io/badge/LangGraph-agent%20workflow-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-demo%20UI-red)
![License](https://img.shields.io/badge/license-MIT-green)


ResumeLens analyzes a resume alongside an optional target job description, then converts the result into a structured improvement workflow. It extracts candidate signals, identifies skill and ATS gaps, rewrites weak content, generates interview preparation prompts, and stores report history and user preferences for future runs.

---

## Table of Contents

- [ResumeLens Demo Video](#resumelens-demo-video)
- [Overview](#overview)
- [Why This Project Matters](#why-this-project-matters)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Mermaid Diagram](#mermaid-diagram)
- [Agent Workflow](#agent-workflow)
- [Tools](#tools)
- [Memory Design](#memory-design)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Sample Request](#sample-request)
- [Sample Response](#sample-response)
- [Testing](#testing)
- [Production-Oriented Engineering Choices](#production-oriented-engineering-choices)
- [Current Scope](#current-scope)
- [Roadmap](#roadmap)
- [Why ResumeLens Is Portfolio-Worthy](#why-resumelens-is-portfolio-worthy)
- [License](#license)

---

## ResumeLens Demo Video

A short walkthrough of ResumeLens showing resume upload, gap analysis with provided job description, and how to improve your current resume. 
https://youtu.be/7OtrqrkBK4s

## Overview

ResumeLens is a backend-first AI application for resume analysis, gap detection, and resume improvement.

At a high level, the system:

- ingests resume content from **text**, **PDF**, **DOCX**, or **TXT**
- accepts an optional job description via **pasted text** or **public job URL**
- extracts a structured candidate profile
- performs deterministic and agent-assisted gap analysis
- generates rewritten resume bullets and improvement guidance
- stores analysis history and report artifacts
- remembers user preferences across runs
- exposes a FastAPI API and a Streamlit interface

ResumeLens is designed to feel like a realistic product workflow rather than a single-endpoint LLM demo.

---

## Why This Project Matters

ResumeLens demonstrates practical **AI backend engineering** using modern application patterns:

- **agent orchestration** with LangGraph
- **structured outputs** enforced through Pydantic schemas
- **tool integration** for resume parsing and job description fetching
- **persistent memory** using PostgreSQL-backed analysis and preferences
- **authentication and protected workflows**
- **production-style API design**, logging, and exception handling
- **dual interface model** with FastAPI backend and Streamlit frontend

This project is intentionally built as a system, not just a prompt wrapper.

---

## Core Features

- Resume ingestion from:
  - pasted text
  - `.txt`
  - `.pdf`
  - `.docx`
- Optional job description input via:
  - pasted text
  - public job URL
- Multi-step LangGraph analysis flow
- Structured candidate profile extraction
- Deterministic job match scoring
- Gap analysis with:
  - strong matches
  - missing skills
  - weak sections
  - ATS keyword gaps
- Resume improvement generation
- Bullet rewriting with style modes:
  - `concise`
  - `technical`
  - `achievement-focused`
- Interview question generation
- Historical improvement tracking across runs
- Analysis history persistence
- User preference memory
- JWT authentication
- Streamlit UI for interactive usage
- GitHub Pages support for project documentation and demo pages

---

## Architecture

### High-Level Architecture

```text
User
  ├── Streamlit UI
  └── API Consumer
          |
          v
     FastAPI API Layer
          |
          v
     Analysis Service
          |
          v
     LangGraph Workflow
      ├── Candidate Profile Agent
      ├── Gap Analysis Agent
      └── Improvement Agent
          |
          v
     Persistence Layer
      ├── User
      ├── Analysis
      ├── Report
      └── UserPreference
          |
          v
      PostgreSQL
```

---

## Mermaid Diagram

```mermaid
flowchart TD
    A[User] --> B[Streamlit UI]
    A --> C[FastAPI API Consumer]

    B --> D[FastAPI Backend]
    C --> D

    D --> E[Auth Layer]
    D --> F[Analysis Endpoint]
    D --> G[History / Reports / Preferences]

    F --> H[Resume Extraction Tool]
    F --> I[Job Description Fetch Tool]
    F --> J[LangGraph Workflow]

    J --> K[Candidate Profile Agent]
    J --> L[Gap Analysis Agent]
    J --> M[Improvement Agent]

    K --> N[Structured Candidate Profile]
    L --> O[Gap Analysis Report]
    M --> P[Final Improvement Report]

    N --> Q[Analysis Service]
    O --> Q
    P --> Q

    Q --> R[(PostgreSQL)]
    G --> R
    E --> R
```

---

## Agent Workflow

### 1. Candidate Profile Extraction
Transforms raw resume content into a structured profile.

Typical outputs:
- candidate name
- contact links
- education
- skills
- projects
- certifications
- inferred seniority
- missing sections

### 2. Gap Analysis
Compares the candidate profile against a target role or job description.

Typical outputs:
- match score
- strong matches
- missing skills
- weak sections
- ATS keyword gaps
- prioritized recommendations

### 3. Resume Improvement
Converts the analysis into actionable resume-improvement output.

Typical outputs:
- rewritten bullets
- ATS keywords
- role-fit feedback
- interview questions
- action plan

---

## Tools

### Resume Extraction Tool
Supports:
- **PDF** via `pypdf`
- **DOCX** via `python-docx`
- **TXT** via UTF-8 decoding

### Job Description Fetch Tool
Fetches public job pages using:
- `requests`
- `beautifulsoup4`

### Skill Normalization Tool
Normalizes related aliases into consistent skill labels.

Examples:
- `Postgres` → `PostgreSQL`
- `fast api` → `FastAPI`
- `js` → `JavaScript`

---

## Memory Design

### Short-Term Memory
Short-term workflow state is handled inside the analysis pipeline during a single run.

This includes:
- normalized resume text
- normalized job description text
- candidate profile
- gap analysis
- final report

### Long-Term Memory
Long-term memory is stored in PostgreSQL.

This includes:
- past analyses
- saved reports
- preferred rewrite style
- preferred target roles
- reusable historical context for improvement tracking

This allows ResumeLens to support repeat usage instead of isolated one-off analysis sessions.

---

## Tech Stack

- **FastAPI**
- **Streamlit**
- **LangGraph**
- **LangChain / OpenAI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Pytest**

---

## Project Structure

```text
resume-copilot/
│
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── analysis.py
│   │           ├── reports.py
│   │           ├── memory.py
│   │           └── health.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── analysis.py
│   │   ├── report.py
│   │   ├── user_preference.py
│   │   └── analysis_memory.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── analysis.py
│   │   
│   |
│   │
│   ├── services/
│   │   ├── analysis_service.py
│   │   ├── report_service.py
|   |   |__ improvement_tracking_service.py
│   │   └── memory_service.py
│   │   
|   |  
│   ├── agents/
│   │   ├── parsing_agent.py
│   │   ├── gap_analysis_agent.py
│   │   └── improvement_agent.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── workflow.py
│   │   
│   │
│   ├── tools/
│   │   ├── resume_extractor.py
│   │   ├── job_fetcher.py
│   │   ├── skill_normalizer.py
│   │   └── text_cleaner.py
│   │
│   ├── repositories/
│   │   ├── preferences.py
│   │   ├── analysis.py
│   │   ├── report.py
│   │   
│   │
│   ├── llm/
│   │   ├── provider.py
│   │   ├── prompts/
│   │   │   ├── parsing_prompts.py
│   │   │   ├── gap_prompts.py
│   │   │   └── improvement_prompts.py
│   │
│   └── main.py
│
├── tests/
│   ├── unit/
│   │   ├── test_resume_extractor.py
│   │   ├── test_skill_normalizer.py
│   │   ├── test_parsing_agent.py
│   │   ├── test_gap_analysis_agent.py
|   |   |__ test_improvement_agent.py
|   |   |__ test_improvement_tracking_service.py
│   │   └── test_improvement_agent.py
│   │
│   ├── integration/
|   |   |__ test_analysis_endpoint.py
│   │   ├── test_analysis_flow.py
│   │   ├── test_auth_endpoints.py
│   │   └── test_report_endpoints.py
│   │
│   └── conftest.py
│
├── alembic/
├── alembic.ini
├── streamlit_app.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SimbaMunatsi/resume-lens.git
cd resume-lens
```

### 2. Create and Activate a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and define the required values.

Example:

```env
APP_NAME=resume-lens
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1
DEBUG=True

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=resume_lens

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/resume_lens

LOG_LEVEL=INFO

SECRET_KEY=your secret key here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MAX_UPLOAD_SIZE_BYTES=2097152
ALLOWED_RESUME_EXTENSIONS=.pdf,.docx,.txt

JOB_FETCH_TIMEOUT_SECONDS=10
MAX_JOB_DESCRIPTION_CHARS=12000

OPENAI_API_KEY=your key here
OPENAI_MODEL=gpt-4.1-mini
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## Running the Application

ResumeLens currently runs as two local processes.

### Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

Backend base URL:

```text
http://127.0.0.1:8000
```

OpenAPI docs:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit frontend

```bash
streamlit run streamlit_app.py
```

By default, the Streamlit app targets:

```text
http://localhost:8000/api/v1
```
---

## API Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Analysis
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/history`

### Reports
- `GET /api/v1/reports/{analysis_id}`

### Memory / Preferences
- `GET /api/v1/memory/preferences`
- `PATCH /api/v1/memory/preferences`

### Health
- `GET /api/v1/health`

---

## Sample Request

### Register User

```json
{
  "username": "simba",
  "email": "simba@example.com",
  "password": "secret123"
}
```

### Run Analysis

This endpoint accepts `multipart/form-data`.

Example fields:
- `resume_text`
- `job_description_text`
- `rewrite_style`
- `target_role`

Example payload:

```text
resume_text=Jane Doe
Backend Engineer
Skills: Python, FastAPI, PostgreSQL
Projects: ResumeLens

job_description_text=Hiring backend engineer with Python, FastAPI, PostgreSQL, Docker.

rewrite_style=technical
target_role=Backend Engineer
```

---

## Sample Response

![Candidate_Profile](assets/profile.png)

```json
{
  "resume_source": "text",
  "resume_filename": null,
  "resume_text": "Jane Doe\nBackend Engineer\nSkills: Python, FastAPI, PostgreSQL\nProjects: ResumeLens",
  "resume_char_count": 84,
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
    "projects": ["ResumeLens"],
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
![Gap analysis](assets/gap_analysis.png)

---

## Testing

Run the full test suite:

```bash
pytest -q
```

The test suite includes:
- unit tests for tools and agents
- integration tests for auth, analysis, reports, and protected routes

![Tests](assets/tests.png)
---


## Production-Oriented Engineering Choices

- structured request logging
- centralized exception handling
- protected JWT endpoints
- deterministic scoring alongside LLM-driven reasoning
- repository and service separation
- persistent analysis and report history
- preference memory for repeated use
- test coverage across unit and integration layers

---

## Current Scope

Future improvements will include:
- Docker
- Docker Compose
- Makefile-based task automation

The project currently runs locally with:

```bash
uvicorn app.main:app --reload
streamlit run streamlit_app.py
```

---

## Roadmap

- downloadable PDF report export
- richer job-description parsing heuristics
- stronger evaluation coverage for parsing and scoring quality
- background job processing for longer analyses
- richer historical comparison views
- cloud deployment pipeline
- stronger GitHub Pages documentation site
- additional UI polish for the Streamlit interface

---

## Why ResumeLens Is Portfolio-Worthy

ResumeLens demonstrates more than simply calling an LLM API.

It shows:
- backend-first AI system design
- agent orchestration with typed outputs
- realistic tool integration
- memory and persistence
- authentication and protected workflows
- structured testing
- a usable UI layer on top of a production-style API

That combination makes it a strong portfolio project for:
- AI backend engineering
- agentic AI systems
- LLM application engineering
- full-stack AI product development

---

## Author
Simbarashe Munatsi

### Contacts
Email : vsmunatsi@gmai.com
LinkedIn : https://www.linkedin.com/in/victor-simbarashe-munatsi/

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
