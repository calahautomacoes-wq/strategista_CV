import json
import os
import threading
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Caminho absoluto: sobe de utils/ para a raiz do projeto
_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV, override=True)

_client: anthropic.Anthropic | None = None
_client_lock = threading.Lock()


def _get_client() -> anthropic.Anthropic:
    """Thread-safe singleton para o cliente Anthropic."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:          # double-checked locking
                _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


_PROMPT = """\
Você é um especialista em recrutamento e seleção. Analise o currículo abaixo e \
retorne APENAS um JSON válido, sem texto adicional, com esta estrutura:

{{
  "nome": "nome completo",
  "email": "email ou vazio",
  "telefone": "telefone ou vazio",
  "cidade_estado": "cidade e estado ou vazio",
  "formacao": "formação acadêmica resumida em uma linha",
  "experiencia": "experiências profissionais resumidas em 2-3 linhas",
  "habilidades": "principais habilidades técnicas e comportamentais",
  "idiomas": "idiomas e níveis ou vazio",
  "resumo": "resumo profissional do candidato em 3-4 frases completas",
  "nota": 7,
  "justificativa": "justificativa objetiva da nota de 1 a 10"
}}

CURRÍCULO:
{cv_text}
"""


def analyze_cv(cv_text: str, filename: str) -> dict:
    """Envia texto do CV ao Claude e retorna análise estruturada."""
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[{"role": "user", "content": _PROMPT.format(cv_text=cv_text[:8000])}],
    )

    raw = message.content[0].text.strip()

    # Remove code fences do markdown, se houver
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(raw)
    data["arquivo"] = filename

    try:
        data["nota"] = float(data.get("nota", 0))
    except (TypeError, ValueError):
        data["nota"] = 0.0

    return data
