# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

StrategisTA is a CV analysis pipeline with a Streamlit frontend. When the user clicks "Buscar CV":
1. Lists PDF/DOCX files from a public MinIO S3 bucket
2. Downloads and extracts text from each file
3. Sends the text to Claude (claude-sonnet-4-6) for structured analysis (name, skills, score 1–10, summary)
4. Appends new rows to a Google Sheet (calahdev@gmail.com), skipping already-processed files
5. Displays results in the Streamlit UI

## Stack

- **Python + Streamlit** — all UI is pure Python
- **Anthropic SDK** (`claude-sonnet-4-6`) — CV analysis and scoring
- **gspread + google-auth-oauthlib** — Google Sheets OAuth2 (Desktop app flow)
- **pdfplumber / python-docx** — text extraction from PDF and DOCX
- **requests** — HTTP calls to the public MinIO S3 API

## Commands

```bash
# First time
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Run
streamlit run main.py

# Specific port
streamlit run main.py --server.port 8502
```

## Project structure

```
main.py              # Home: hero, metrics, "Buscar CV" button, processing log
pages/
  1_Curriculos.py    # CV viewer: cards, table, and bar chart tabs
utils/
  minio_client.py    # list_cv_files(), download_file() — S3 XML API, no auth
  cv_parser.py       # extract_text() — pdfplumber for PDF, python-docx for DOCX
  cv_analyzer.py     # analyze_cv() — sends text to Claude, returns structured dict
  sheets.py          # get_processed_files(), append_cv(), get_all_cvs() — gspread
components/
  metrics.py         # metric_row() helper (currently unused by main pages)
.streamlit/
  config.toml        # Blue/white theme and server settings
.env                 # ANTHROPIC_API_KEY and MinIO config (not committed)
credentials.json     # Google OAuth2 Desktop credentials (not committed)
token.json           # Saved OAuth2 token after first login (not committed)
```

## Required secrets (not committed)

| File / Variable | Purpose |
|---|---|
| `.env` → `ANTHROPIC_API_KEY` | Anthropic API key |
| `.env` → `MINIO_API_ENDPOINT` | MinIO S3 API base URL (defaults to `https://bots-strategista-minio.1eybor.easypanel.host`) |
| `credentials.json` | Google OAuth2 client credentials (Desktop app type, from Google Cloud Console) |
| `token.json` | Auto-generated on first Google login — do not edit manually |

## Google Sheets setup

1. Google Cloud Console → create project → enable **Google Sheets API** and **Google Drive API**
2. Credentials → Create OAuth 2.0 Client ID → type **Desktop app** → download JSON → save as `credentials.json`
3. First `streamlit run main.py` → click Buscar CV → browser opens for Google login with **calahdev@gmail.com**
4. Sheet named `StrategisTA - Currículos` is created automatically

## Duplicate prevention

`sheets.py:get_processed_files()` fetches column A (Arquivo) from the sheet and returns a set of filenames. In `main.py`, files in that set are skipped before downloading or calling the API.

## Adding a new page

Create `pages/N_Name.py`. Must call `st.set_page_config()` as the first Streamlit call. Appears in the sidebar automatically.
