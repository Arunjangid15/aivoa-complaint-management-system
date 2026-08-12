"""
Very small, dependency-light document -> plain text extractor.
Assignment explicitly says production-grade OCR/parsing is NOT required,
so this covers the common formats only: PDF, DOCX, TXT, EML.
"""
import io
import email
from email import policy
from pypdf import PdfReader
from docx import Document


def extract_text_from_upload(filename: str, content: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == "docx":
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == "eml":
        msg = email.message_from_bytes(content, policy=policy.default)
        parts = []
        if msg["subject"]:
            parts.append(f"Subject: {msg['subject']}")
        if msg["from"]:
            parts.append(f"From: {msg['from']}")
        body = msg.get_body(preferencelist=("plain", "html"))
        if body:
            parts.append(body.get_content())
        return "\n".join(parts)

    # txt or anything else: just decode
    return content.decode("utf-8", errors="ignore")
