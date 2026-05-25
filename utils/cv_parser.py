import base64
import io
import fitz          # PyMuPDF — converte páginas PDF em imagem
import pdfplumber
from docx import Document


def extract_text(content: bytes, filename: str) -> str:
    """Extrai texto de PDF ou DOCX. Para PDFs escaneados usa OCR via Claude Vision."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return _from_pdf(content)
    if name.endswith(".docx"):
        return _from_docx(content)
    return content.decode("utf-8", errors="ignore")


# ── PDF ───────────────────────────────────────────────────────────────────────

def _from_pdf(content: bytes) -> str:
    """Tenta extração nativa; se falhar, aplica OCR via Claude Vision."""
    text = _pdf_native_text(content)
    if text:
        return text
    # PDF escaneado → converter para imagens e usar Claude Vision
    return _pdf_ocr_claude(content)


def _pdf_native_text(content: bytes) -> str:
    """Extração direta de texto via pdfplumber (rápida, sem custo extra)."""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages).strip()
    except Exception:
        return ""


def _pdf_ocr_claude(content: bytes) -> str:
    """
    Converte cada página do PDF em PNG com PyMuPDF e envia ao Claude Vision
    para extrair o texto. Processa no máximo 10 páginas para controlar custo.
    """
    from utils.cv_analyzer import _get_client   # importação local para evitar ciclo

    doc = fitz.open(stream=content, filetype="pdf")
    MAX_PAGES = 10
    page_texts: list[str] = []

    client = _get_client()

    for page_num in range(min(len(doc), MAX_PAGES)):
        page = doc[page_num]
        # Renderiza a página em 150 DPI (boa resolução sem exceder limite de tokens)
        mat  = fitz.Matrix(150 / 72, 150 / 72)
        pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        img_bytes  = pix.tobytes("png")
        img_b64    = base64.standard_b64encode(img_bytes).decode()

        response = client.messages.create(
            model="claude-haiku-4-5",          # Haiku: mais rápido e barato para OCR
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Esta é uma página de um currículo. "
                            "Extraia TODO o texto visível, preservando a estrutura. "
                            "Retorne apenas o texto extraído, sem comentários."
                        ),
                    },
                ],
            }],
        )
        page_texts.append(response.content[0].text.strip())

    doc.close()
    result = "\n\n".join(t for t in page_texts if t)
    if not result:
        raise ValueError("Não foi possível extrair texto do PDF (nem por OCR).")
    return result


# ── DOCX ──────────────────────────────────────────────────────────────────────

def _from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
