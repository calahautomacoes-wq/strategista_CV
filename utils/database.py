import os
import pandas as pd
from supabase import create_client, Client
from pathlib import Path
from dotenv import load_dotenv

_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV, override=True)

_TABLE = "curriculos"
_client: Client | None = None

_COLUMNS = [
    "arquivo", "data_analise", "nome", "email", "telefone",
    "cidade_estado", "formacao", "experiencia", "habilidades",
    "idiomas", "resumo", "nota", "justificativa",
]


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY precisam estar no .env")
        _client = create_client(url, key)
    return _client


def get_processed_files() -> set[str]:
    """Return set of filenames already recorded in the database."""
    resp = _get_client().table(_TABLE).select("arquivo").execute()
    return {row["arquivo"] for row in resp.data} if resp.data else set()


def _to_record(data: dict, timestamp: str) -> dict:
    """Converte dict analisado para formato do banco de dados."""
    return {
        "arquivo":       data.get("arquivo", ""),
        "data_analise":  timestamp,
        "nome":          data.get("nome", ""),
        "email":         data.get("email", ""),
        "telefone":      data.get("telefone", ""),
        "cidade_estado": data.get("cidade_estado", ""),
        "formacao":      data.get("formacao", ""),
        "experiencia":   data.get("experiencia", ""),
        "habilidades":   data.get("habilidades", ""),
        "idiomas":       data.get("idiomas", ""),
        "resumo":        data.get("resumo", ""),
        "nota":          float(data.get("nota", 0) or 0),
        "justificativa": data.get("justificativa", ""),
    }


def insert_cv(data: dict, timestamp: str) -> None:
    """Insere um único CV no banco de dados."""
    _get_client().table(_TABLE).insert(_to_record(data, timestamp)).execute()


def batch_insert_cvs(items: list[tuple[dict, str]]) -> None:
    """Insere múltiplos CVs em um único request ao Supabase."""
    if not items:
        return
    records = [_to_record(data, ts) for data, ts in items]
    _get_client().table(_TABLE).insert(records).execute()


def get_all_cvs() -> pd.DataFrame:
    """Return all CV records as a DataFrame ordered by score desc."""
    resp = (
        _get_client()
        .table(_TABLE)
        .select("*")
        .order("nota", desc=True)
        .execute()
    )
    if not resp.data:
        return pd.DataFrame(columns=_COLUMNS)

    df = pd.DataFrame(resp.data)
    rename = {
        "data_analise":  "Data de Análise",
        "arquivo":       "Arquivo",
        "nome":          "Nome",
        "email":         "Email",
        "telefone":      "Telefone",
        "cidade_estado": "Cidade/Estado",
        "formacao":      "Formação",
        "experiencia":   "Experiência",
        "habilidades":   "Habilidades",
        "idiomas":       "Idiomas",
        "resumo":        "Resumo",
        "nota":          "Nota",
        "justificativa": "Justificativa",
    }
    df = df.rename(columns=rename)
    df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")
    keep = list(rename.values())
    return df[[c for c in keep if c in df.columns]]
