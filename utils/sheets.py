import gspread
import pandas as pd

_SPREADSHEET_NAME = "StrategisTA - Currículos"
_SHEET_HEADERS = [
    "Arquivo", "Data de Análise", "Nome", "Email", "Telefone",
    "Cidade/Estado", "Formação", "Experiência", "Habilidades",
    "Idiomas", "Resumo", "Nota", "Justificativa",
]


def _get_sheet() -> gspread.Worksheet:
    gc = gspread.oauth(
        credentials_filename="credentials.json",
        authorized_user_filename="token.json",
    )
    try:
        spreadsheet = gc.open(_SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(_SPREADSHEET_NAME)
        # Share with the designated account so it's accessible there
        spreadsheet.share("calahdev@gmail.com", perm_type="user", role="writer")

    sheet = spreadsheet.sheet1
    if not sheet.get_all_values():
        sheet.append_row(_SHEET_HEADERS, value_input_option="RAW")
    return sheet


def get_processed_files() -> set[str]:
    """Return set of filenames already recorded in the sheet."""
    sheet = _get_sheet()
    rows = sheet.get_all_values()
    return {row[0] for row in rows[1:] if row} if len(rows) > 1 else set()


def append_cv(data: dict, timestamp: str) -> None:
    """Append one CV row to the sheet."""
    sheet = _get_sheet()
    sheet.append_row(
        [
            data.get("arquivo", ""),
            timestamp,
            data.get("nome", ""),
            data.get("email", ""),
            data.get("telefone", ""),
            data.get("cidade_estado", ""),
            data.get("formacao", ""),
            data.get("experiencia", ""),
            data.get("habilidades", ""),
            data.get("idiomas", ""),
            data.get("resumo", ""),
            data.get("nota", ""),
            data.get("justificativa", ""),
        ],
        value_input_option="RAW",
    )


def get_all_cvs() -> pd.DataFrame:
    """Return all CV rows as a DataFrame."""
    sheet = _get_sheet()
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return pd.DataFrame(columns=_SHEET_HEADERS)
    df = pd.DataFrame(rows[1:], columns=_SHEET_HEADERS)
    df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")
    return df
