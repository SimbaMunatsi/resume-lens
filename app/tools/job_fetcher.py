from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.tools.text_cleaner import clean_text


class JobFetchError(Exception):
    """Raised when job description fetching or parsing fails."""


def validate_job_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise JobFetchError("Invalid job URL. Provide a valid http or https URL.")


def fetch_job_page(url: str) -> str:
    validate_job_url(url)

    try:
        response = requests.get(
            url,
            timeout=settings.JOB_FETCH_TIMEOUT_SECONDS,
            headers={
                "User-Agent": (
                    "ResumeCopilot/0.1 "
                    "(Job Description Fetcher for educational portfolio project)"
                )
            },
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise JobFetchError("Job URL fetch timed out.") from exc
    except requests.RequestException as exc:
        raise JobFetchError("Failed to fetch job URL.") from exc

    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        raise JobFetchError("Job URL did not return an HTML page.")

    return response.text


def extract_job_text_from_html(html: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "svg", "img"]):
            tag.decompose()

        main_candidates = [
            soup.find("main"),
            soup.find("article"),
            soup.find(attrs={"role": "main"}),
        ]

        chosen_root = next((candidate for candidate in main_candidates if candidate), soup)

        text = chosen_root.get_text(separator="\n", strip=True)
        text = clean_text(text)

        if not text:
            raise JobFetchError("No readable job description text found on the page.")

        if len(text) > settings.MAX_JOB_DESCRIPTION_CHARS:
            text = text[: settings.MAX_JOB_DESCRIPTION_CHARS].rstrip()

        return text
    except JobFetchError:
        raise
    except Exception as exc:
        raise JobFetchError("Failed to parse job description page.") from exc


def fetch_job_description_text(url: str) -> str:
    html = fetch_job_page(url)
    return extract_job_text_from_html(html)