from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.core.config import settings
from app.tools.text_cleaner import clean_text


class ResumeExtractionError(Exception):
    """Raised when resume extraction fails."""


def validate_file_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.allowed_resume_extensions:
        allowed = ", ".join(sorted(settings.allowed_resume_extensions))
        raise ResumeExtractionError(
            f"Unsupported file type '{suffix}'. Allowed types: {allowed}"
        )
    return suffix


def validate_file_size(file_bytes: bytes) -> None:
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise ResumeExtractionError(
            f"File too large. Maximum allowed size is "
            f"{settings.MAX_UPLOAD_SIZE_BYTES} bytes."
        )


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ResumeExtractionError("Failed to decode TXT file as UTF-8.") from exc


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_stream = BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:
        raise ResumeExtractionError("Failed to extract text from PDF file.") from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        docx_stream = BytesIO(file_bytes)
        document = Document(docx_stream)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs)
    except Exception as exc:
        raise ResumeExtractionError("Failed to extract text from DOCX file.") from exc


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    suffix = validate_file_extension(filename)
    validate_file_size(file_bytes)

    if suffix == ".txt":
        raw_text = extract_text_from_txt(file_bytes)
    elif suffix == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif suffix == ".docx":
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raise ResumeExtractionError("Unsupported file type.")

    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        raise ResumeExtractionError("No readable text could be extracted from the file.")

    return cleaned_text