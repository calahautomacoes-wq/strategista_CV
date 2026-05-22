# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Python + Streamlit** — all UI is pure Python, no HTML/CSS/JS needed
- **Plotly** for interactive charts
- **Pandas** for data manipulation
- **openpyxl** for Excel file support

## Commands

```bash
# Create and activate virtual environment (first time)
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py

# Run on a specific port
streamlit run main.py --server.port 8502
```

## Architecture

```
main.py              # Home page — runs via `streamlit run main.py`
pages/               # Each file = one sidebar page (Streamlit native multi-page)
components/          # Reusable UI functions (e.g., metric_row)
utils/               # Data loading helpers (cached with @st.cache_data)
data/                # Local data files (CSV, Excel) — not committed to git
.streamlit/config.toml  # Theme and server settings
```

### Multi-page conventions

- Page files in `pages/` are named `N_Page_Name.py` (number prefix controls sidebar order).
- Every page file must call `st.set_page_config()` as its first Streamlit call.
- Pages import from `components/` and `utils/` using standard Python imports.

### Data loading

`utils/data.py` exposes `load_csv` and `load_excel`, both decorated with `@st.cache_data` so data is read once per session. Drop data files into `data/` and load them via these helpers.

### Adding a new page

1. Create `pages/N_Name.py` with `st.set_page_config` at the top.
2. Import reusable components from `components/` as needed.
3. The file appears automatically in the sidebar — no routing config required.
