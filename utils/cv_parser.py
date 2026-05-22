import io
import pdfplumber
from docx import Document


def extract_text(content: bytes, filename: str) -> str:
    """Extract plain text from PDF or DOCX file content."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return _from_pdf(content)
    if name.endswith(".docx"):
        return _from_docx(content)
    # Fallback: treat as UTF-8 text
    return content.decode("utf-8", errors="ignore")


def _from_pdf(content: bytes) -> str:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("PDF parece ser baseado em imagem — texto não pôde ser extraído.")
    return text


def _from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
