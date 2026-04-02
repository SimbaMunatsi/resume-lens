import json
import os
from typing import Any

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def get_api_base_url() -> str:
    env_value = os.getenv("API_BASE_URL")
    if env_value:
        return env_value

    try:
        return st.secrets["API_BASE_URL"]
    except (StreamlitSecretNotFoundError, KeyError, FileNotFoundError):
        return "http://localhost:8000/api/v1"


API_BASE_URL = get_api_base_url()


def api_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
        timeout=20,
    )

    if response.ok:
        return True, "Registration successful. You can now log in."

    try:
        detail = response.json().get("detail", "Registration failed.")
    except Exception:
        detail = "Registration failed."
    return False, detail


def login_user(email: str, password: str) -> tuple[bool, str]:
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password,
        },
        timeout=20,
    )

    if response.ok:
        data = response.json()
        st.session_state["access_token"] = data["access_token"]
        st.session_state["user_email"] = email
        return True, "Login successful."

    try:
        detail = response.json().get("detail", "Login failed.")
    except Exception:
        detail = "Login failed."
    return False, detail


def run_analysis(
    *,
    resume_text: str | None,
    resume_file,
    job_description_text: str | None,
    job_url: str | None,
    rewrite_style: str,
    target_role: str | None,
) -> tuple[bool, dict[str, Any] | str]:
    data = {
        "rewrite_style": rewrite_style,
    }

    if target_role:
        data["target_role"] = target_role

    if resume_text:
        data["resume_text"] = resume_text

    if job_description_text:
        data["job_description_text"] = job_description_text

    if job_url:
        data["job_url"] = job_url

    files = None
    if resume_file is not None:
        files = {
            "resume_file": (
                resume_file.name,
                resume_file.getvalue(),
                resume_file.type or "application/octet-stream",
            )
        }

    response = requests.post(
        f"{API_BASE_URL}/analysis/run",
        headers=api_headers(),
        data=data,
        files=files,
        timeout=120,
    )

    if response.ok:
        return True, response.json()

    try:
        detail = response.json().get("detail", "Analysis failed.")
    except Exception:
        detail = "Analysis failed."
    return False, detail


def get_history() -> tuple[bool, list[dict[str, Any]] | str]:
    response = requests.get(
        f"{API_BASE_URL}/analysis/history",
        headers=api_headers(),
        timeout=20,
    )

    if response.ok:
        return True, response.json()

    try:
        detail = response.json().get("detail", "Failed to load history.")
    except Exception:
        detail = "Failed to load history."
    return False, detail


def get_report(analysis_id: int) -> tuple[bool, dict[str, Any] | str]:
    response = requests.get(
        f"{API_BASE_URL}/reports/{analysis_id}",
        headers=api_headers(),
        timeout=20,
    )

    if response.ok:
        return True, response.json()

    try:
        detail = response.json().get("detail", "Failed to load report.")
    except Exception:
        detail = "Failed to load report."
    return False, detail


def get_preferences() -> tuple[bool, dict[str, Any] | str]:
    response = requests.get(
        f"{API_BASE_URL}/memory/preferences",
        headers=api_headers(),
        timeout=20,
    )

    if response.ok:
        return True, response.json()

    try:
        detail = response.json().get("detail", "Failed to load preferences.")
    except Exception:
        detail = "Failed to load preferences."
    return False, detail


def update_preferences(
    preferred_rewrite_style: str | None,
    preferred_target_roles: list[str] | None,
) -> tuple[bool, dict[str, Any] | str]:
    payload: dict[str, Any] = {}
    if preferred_rewrite_style:
        payload["preferred_rewrite_style"] = preferred_rewrite_style
    if preferred_target_roles is not None:
        payload["preferred_target_roles"] = preferred_target_roles

    response = requests.patch(
        f"{API_BASE_URL}/memory/preferences",
        headers={**api_headers(), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=20,
    )

    if response.ok:
        return True, response.json()

    try:
        detail = response.json().get("detail", "Failed to update preferences.")
    except Exception:
        detail = "Failed to update preferences."
    return False, detail


def render_auth_section() -> None:
    st.subheader("Authentication")

    auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])

    with auth_tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            if submitted:
                ok, message = login_user(email, password)
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with auth_tab2:
        with st.form("register_form"):
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Register")
            if submitted:
                ok, message = register_user(username, email, password)
                if ok:
                    st.success(message)
                else:
                    st.error(message)


def render_profile(candidate_profile: dict[str, Any]) -> None:
    st.subheader("Candidate Profile")
    st.json(candidate_profile)


def render_gap_analysis(gap_analysis: dict[str, Any]) -> None:
    st.subheader("Gap Analysis")

    c1, c2, c3 = st.columns(3)
    c1.metric("Match Score", gap_analysis.get("match_score", 0))
    c2.metric("Missing Skills", len(gap_analysis.get("missing_skills", [])))
    c3.metric("ATS Gaps", len(gap_analysis.get("ats_keyword_gaps", [])))

    st.markdown("**Strong Matches**")
    st.write(gap_analysis.get("strong_matches", []))

    st.markdown("**Missing Skills**")
    st.write(gap_analysis.get("missing_skills", []))

    st.markdown("**Weak Sections**")
    st.write(gap_analysis.get("weak_sections", []))

    st.markdown("**Top Recommendations**")
    st.write(gap_analysis.get("top_recommendations", []))

    if gap_analysis.get("scoring_notes"):
        st.info(gap_analysis["scoring_notes"])


def render_final_report(final_report: dict[str, Any]) -> None:
    st.subheader("Final Report")

    st.markdown("### Summary")
    st.write(final_report.get("summary", ""))

    st.markdown("### Strengths")
    st.write(final_report.get("strengths", []))

    st.markdown("### Weaknesses")
    st.write(final_report.get("weaknesses", []))

    st.markdown("### Rewritten Bullets")
    for bullet in final_report.get("rewritten_bullets", []):
        st.markdown(f"- {bullet}")

    st.markdown("### ATS Keywords")
    st.write(final_report.get("ats_keywords", []))

    st.markdown("### Role Fit Feedback")
    st.write(final_report.get("role_fit_feedback", ""))

    st.markdown("### Interview Questions")
    for question in final_report.get("interview_questions", []):
        st.markdown(f"- {question}")

    st.markdown("### Action Plan")
    for action in final_report.get("action_plan", []):
        st.markdown(f"- {action}")


def render_historical_improvement(historical_improvement: dict[str, Any] | None) -> None:
    st.subheader("Historical Improvement Tracking")

    if not historical_improvement:
        st.info("No previous analysis found yet. Run another analysis to unlock progress tracking.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Previous Score",
        historical_improvement.get("previous_match_score"),
    )
    c2.metric(
        "Current Score",
        historical_improvement.get("current_match_score"),
        delta=historical_improvement.get("score_change"),
    )
    c3.metric(
        "ATS Gap Count",
        historical_improvement.get("current_ats_gap_count"),
    )

    st.markdown("**Improved Areas**")
    st.write(historical_improvement.get("improved_areas", []))

    st.markdown("**Repeated Weaknesses**")
    st.write(historical_improvement.get("repeated_weaknesses", []))

    st.markdown("**Resolved Weaknesses**")
    st.write(historical_improvement.get("resolved_weaknesses", []))

    if historical_improvement.get("summary"):
        st.success(historical_improvement["summary"])


def render_analysis_tab() -> None:
    st.subheader("Run Analysis")

    input_mode = st.radio(
        "Resume Input Mode",
        options=["Paste Text", "Upload File"],
        horizontal=True,
    )

    resume_text = None
    resume_file = None

    if input_mode == "Paste Text":
        resume_text = st.text_area("Resume Text", height=250)
    else:
        resume_file = st.file_uploader(
            "Upload Resume",
            type=["txt", "pdf", "docx"],
        )

    jd_mode = st.radio(
        "Job Description Input",
        options=["None", "Paste JD Text", "Job URL"],
        horizontal=True,
    )

    job_description_text = None
    job_url = None

    if jd_mode == "Paste JD Text":
        job_description_text = st.text_area("Job Description Text", height=180)
    elif jd_mode == "Job URL":
        job_url = st.text_input("Job URL")

    rewrite_style = st.selectbox(
        "Rewrite Style",
        options=["concise", "technical", "achievement-focused"],
    )

    target_role = st.text_input("Target Role (optional)", placeholder="Backend Engineer")

    if st.button("Run Resume Analysis", type="primary"):
        if input_mode == "Paste Text" and not resume_text:
            st.error("Please provide resume text.")
            return
        if input_mode == "Upload File" and resume_file is None:
            st.error("Please upload a resume file.")
            return

        with st.spinner("Running analysis..."):
            ok, result = run_analysis(
                resume_text=resume_text,
                resume_file=resume_file,
                job_description_text=job_description_text,
                job_url=job_url,
                rewrite_style=rewrite_style,
                target_role=target_role or None,
            )

        if not ok:
            st.error(str(result))
            return

        st.success("Analysis completed.")
        render_profile(result.get("candidate_profile") or {})
        render_gap_analysis(result.get("gap_analysis") or {})
        render_final_report(result.get("final_report") or {})
        render_historical_improvement(result.get("historical_improvement"))


def render_history_tab() -> None:
    st.subheader("Analysis History")

    ok, result = get_history()
    if not ok:
        st.error(str(result))
        return

    history = result
    if not history:
        st.info("No saved analyses yet.")
        return

    for item in history:
        with st.expander(
            f"Analysis #{item['id']} | score={item.get('match_score')} | role={item.get('target_role') or 'n/a'}"
        ):
            st.write(f"Resume file: {item.get('resume_filename')}")
            st.write(f"Rewrite style: {item.get('rewrite_style')}")
            st.write(f"Created at: {item.get('created_at')}")

            if st.button(f"Load Report #{item['id']}", key=f"load_report_{item['id']}"):
                ok_report, report_result = get_report(item["id"])
                if not ok_report:
                    st.error(str(report_result))
                else:
                    st.session_state["loaded_report"] = report_result

    loaded_report = st.session_state.get("loaded_report")
    if loaded_report:
        st.markdown("---")
        st.subheader(f"Saved Report: Analysis #{loaded_report['analysis_id']}")
        render_final_report(loaded_report["final_report"])


def render_preferences_tab() -> None:
    st.subheader("Preferences")

    ok, result = get_preferences()
    if not ok:
        st.error(str(result))
        return

    current = result

    with st.form("preferences_form"):
        rewrite_style = st.selectbox(
            "Preferred Rewrite Style",
            options=["concise", "technical", "achievement-focused"],
            index=["concise", "technical", "achievement-focused"].index(
                current.get("preferred_rewrite_style") or "concise"
            ),
        )

        target_roles_text = st.text_area(
            "Preferred Target Roles (one per line)",
            value="\n".join(current.get("preferred_target_roles", [])),
            height=120,
        )

        submitted = st.form_submit_button("Save Preferences")
        if submitted:
            preferred_target_roles = [
                line.strip()
                for line in target_roles_text.splitlines()
                if line.strip()
            ]

            ok_update, update_result = update_preferences(
                preferred_rewrite_style=rewrite_style,
                preferred_target_roles=preferred_target_roles,
            )

            if ok_update:
                st.success("Preferences updated.")
                st.rerun()
            else:
                st.error(str(update_result))

    st.markdown("### Current Memory Snapshot")
    st.json(current)


def main() -> None:
    st.set_page_config(
        page_title="ResumeCopilot",
        page_icon="📄",
        layout="wide",
    )

    st.title("ResumeCopilot")
    st.caption("AI-powered resume analyzer with LangGraph agents, memory, and persistence.")

    with st.sidebar:
        st.markdown("### Backend")
        st.code(API_BASE_URL)

        if st.session_state.get("access_token"):
            st.success(f"Logged in as {st.session_state.get('user_email')}")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        else:
            st.warning("Not logged in")

    if not st.session_state.get("access_token"):
        render_auth_section()
        return

    tab1, tab2, tab3 = st.tabs(["Run Analysis", "History", "Preferences"])

    with tab1:
        render_analysis_tab()

    with tab2:
        render_history_tab()

    with tab3:
        render_preferences_tab()


if __name__ == "__main__":
    main()