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


# Modelo e limite de texto para análise de CVs.
# claude-haiku-4-5  → ~3× mais barato que claude-sonnet-4-6 ($1/$5 vs $3/$15 por 1M tokens)
# CV_CHAR_LIMIT     → a maioria dos CVs tem as informações relevantes nos primeiros ~5 000 chars
_MODEL     = "claude-haiku-4-5"
_CV_CHAR_LIMIT = 5_000

_SYSTEM = """\
Você é um especialista em recrutamento e seleção. Analise o currículo fornecido e \
retorne APENAS um JSON válido, sem texto adicional, com esta estrutura:

{
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
  "justificativa": "justificativa objetiva da nota de 1 a 10",
  "sexo": "masculino"
}

Para o campo "sexo": analise o primeiro nome do candidato e infira o gênero mais provável \
com base em nomes tipicamente brasileiros. Use "masculino", "feminino" ou "prefiro não dizer". \
Em caso de dúvida (nome ambíguo, estrangeiro ou não identificado), use "prefiro não dizer"."""


def analyze_cv(cv_text: str, filename: str) -> dict:
    """Envia texto do CV ao Claude e retorna análise estruturada."""
    message = _get_client().messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"CURRÍCULO:\n{cv_text[:_CV_CHAR_LIMIT]}",
        }],
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

    # Normaliza o campo sexo
    sexo_raw = str(data.get("sexo", "")).strip().lower()
    if sexo_raw in ("masculino", "male", "m"):
        data["sexo"] = "masculino"
    elif sexo_raw in ("feminino", "female", "f"):
        data["sexo"] = "feminino"
    else:
        data["sexo"] = "prefiro não dizer"

    return data
