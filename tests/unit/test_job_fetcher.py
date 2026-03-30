import pytest
import requests

from app.tools.job_fetcher import (
    JobFetchError,
    extract_job_text_from_html,
    fetch_job_description_text,
)


class MockResponse:
    def __init__(self, text: str, status_code: int = 200, content_type: str = "text/html"):
        self.text = text
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_extract_job_text_from_html_success() -> None:
    html = """
    <html>
        <body>
            <main>
                <h1>Backend Engineer</h1>
                <p>We are hiring a Python backend engineer.</p>
                <p>Required: FastAPI, PostgreSQL, Docker.</p>
            </main>
        </body>
    </html>
    """

    text = extract_job_text_from_html(html)

    assert "Backend Engineer" in text
    assert "FastAPI" in text
    assert "PostgreSQL" in text


def test_extract_job_text_from_html_removes_scripts() -> None:
    html = """
    <html>
        <body>
            <script>alert("ignore");</script>
            <main>
                <h1>ML Engineer</h1>
                <p>Experience with Python and LLM systems.</p>
            </main>
        </body>
    </html>
    """

    text = extract_job_text_from_html(html)

    assert 'alert("ignore")' not in text
    assert "ML Engineer" in text


def test_fetch_job_description_text_success(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html>
        <body>
            <main>
                <h1>Data Engineer</h1>
                <p>Build ETL pipelines and SQL systems.</p>
            </main>
        </body>
    </html>
    """

    def mock_get(*args, **kwargs):
        return MockResponse(text=html)

    monkeypatch.setattr("app.tools.job_fetcher.requests.get", mock_get)

    text = fetch_job_description_text("https://example.com/job")

    assert "Data Engineer" in text
    assert "ETL" in text


def test_fetch_job_description_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args, **kwargs):
        raise requests.Timeout("timed out")

    monkeypatch.setattr("app.tools.job_fetcher.requests.get", mock_get)

    with pytest.raises(JobFetchError, match="timed out"):
        fetch_job_description_text("https://example.com/job")


def test_fetch_job_description_bad_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args, **kwargs):
        return MockResponse(text="Not found", status_code=404)

    monkeypatch.setattr("app.tools.job_fetcher.requests.get", mock_get)

    with pytest.raises(JobFetchError, match="Failed to fetch job URL"):
        fetch_job_description_text("https://example.com/job")


def test_fetch_job_description_invalid_url() -> None:
    with pytest.raises(JobFetchError, match="Invalid job URL"):
        fetch_job_description_text("not-a-real-url")


def test_fetch_job_description_non_html(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args, **kwargs):
        return MockResponse(text="{}", content_type="application/json")

    monkeypatch.setattr("app.tools.job_fetcher.requests.get", mock_get)

    with pytest.raises(JobFetchError, match="did not return an HTML page"):
        fetch_job_description_text("https://example.com/job")