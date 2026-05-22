import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
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
    """Send CV text to Claude and return structured analysis."""
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[{"role": "user", "content": _PROMPT.format(cv_text=cv_text[:8000])}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(raw)
    data["arquivo"] = filename

    # Ensure nota is numeric
    try:
        data["nota"] = float(data.get("nota", 0))
    except (TypeError, ValueError):
        data["nota"] = 0.0

    return data
