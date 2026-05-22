import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="StrategisTA",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}

  .stApp {
    background: #EFF6FF;
  }

  /* Hero banner */
  .hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 65%, #3B82F6 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(37,99,235,0.35);
    position: relative;
    overflow: hidden;
  }
  .hero::after {
    content: '';
    position: absolute;
    width: 350px; height: 350px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    top: -80px; right: -60px;
  }
  .hero h1 {
    color: #fff;
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -1.5px;
  }
  .hero p {
    color: #BFDBFE;
    margin: 0.4rem 0 0;
    font-size: 1rem;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #fff;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
  }

  /* Metric cards */
  .card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE;
  }
  .card-icon { font-size: 1.6rem; margin-bottom: 6px; }
  .card-val  { font-size: 2.4rem; font-weight: 800; color: #1E40AF; line-height: 1.1; }
  .card-lbl  { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

  /* Action card */
  .action-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE;
    text-align: center;
  }
  .action-title { font-size: 1.1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.3rem; }
  .action-desc  { font-size: 0.85rem; color: #64748B; margin-bottom: 1.2rem; }

  /* Primary button override */
  div[data-testid="stButton"] > button[kind="primary"],
  div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.4px !important;
    width: 100% !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.4) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
  }
  div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(37,99,235,0.5) !important;
  }

  /* Log terminal */
  .terminal {
    background: #0F172A;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    max-height: 280px;
    overflow-y: auto;
    margin-top: 1rem;
  }
  .t-ok   { color: #34D399; }
  .t-info { color: #38BDF8; }
  .t-warn { color: #FCD34D; }
  .t-err  { color: #F87171; }
  .t-dim  { color: #475569; }

  /* Setup warning */
  .setup-box {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
  }

  /* Section header */
  .section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1E3A8A;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 6px;
    border-bottom: 2px solid #DBEAFE;
  }
</style>
""", unsafe_allow_html=True)

# ── Setup check ───────────────────────────────────────────────────────────────
_missing_setup = []
if not Path(".env").exists() or "sua_chave_aqui" in Path(".env").read_text():
    _missing_setup.append("**ANTHROPIC_API_KEY** não configurada no arquivo `.env`")
if not Path("credentials.json").exists():
    _missing_setup.append("**credentials.json** do Google não encontrado na raiz do projeto")

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">StrategisTA</div>
  <h1>📋 Análise de Currículos</h1>
  <p>Busca automática, análise com IA e registro em planilha — tudo em um clique.</p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def _load_metrics():
    try:
        from utils.sheets import get_all_cvs
        df = get_all_cvs()
        total = len(df)
        media = round(df["Nota"].mean(), 1) if total else "—"
        ultima = df["Data de Análise"].iloc[-1] if total else "—"
        return total, media, ultima
    except Exception:
        return "—", "—", "—"

total_cvs, media_nota, ultima_data = _load_metrics()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="card">
        <div class="card-icon">📄</div>
        <div class="card-val">{total_cvs}</div>
        <div class="card-lbl">Currículos analisados</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="card">
        <div class="card-icon">⭐</div>
        <div class="card-val">{media_nota}</div>
        <div class="card-lbl">Nota média</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="card">
        <div class="card-icon">🕐</div>
        <div class="card-val" style="font-size:1.2rem; padding-top:0.6rem">{ultima_data}</div>
        <div class="card-lbl">Última análise</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Ações</div>', unsafe_allow_html=True)

# ── Action panel ──────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 2], gap="large")

with col_btn:
    st.markdown("""<div class="action-card">
        <div class="action-title">Buscar novos currículos</div>
        <div class="action-desc">Verifica o repositório MinIO e processa apenas os arquivos ainda não analisados.</div>
    </div>""", unsafe_allow_html=True)
    # Spacer between card bg and button (button renders outside the div)
    buscar = st.button("🔍  Buscar CV", use_container_width=True)

with col_info:
    if _missing_setup:
        st.markdown('<div class="setup-box">', unsafe_allow_html=True)
        st.warning("**Configuração pendente** — resolva antes de buscar:")
        for item in _missing_setup:
            st.markdown(f"- {item}")
        st.markdown("""
**Passos para configurar o Google:**
1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto e habilite **Google Sheets API** e **Google Drive API**
3. Em *Credenciais*, crie um *OAuth 2.0 Client ID* do tipo **Desktop app**
4. Baixe o JSON e salve como `credentials.json` na raiz do projeto
5. Na primeira execução, um navegador abrirá para login com **calahdev@gmail.com**
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Sistema configurado. Clique em **Buscar CV** para iniciar a análise. Apenas currículos novos serão processados — os já registrados na planilha serão ignorados.")

# ── Processing ────────────────────────────────────────────────────────────────
if buscar:
    if _missing_setup:
        st.error("Corrija os itens de configuração acima antes de continuar.")
        st.stop()

    log_lines: list[str] = []
    log_placeholder = st.empty()

    def render_log():
        html = '<div class="terminal">' + "".join(log_lines) + "</div>"
        log_placeholder.markdown(html, unsafe_allow_html=True)

    def log(msg: str, kind: str = "info"):
        css = {"ok": "t-ok", "info": "t-info", "warn": "t-warn", "err": "t-err", "dim": "t-dim"}.get(kind, "t-info")
        ts = datetime.now().strftime("%H:%M:%S")
        log_lines.append(f'<div><span class="t-dim">[{ts}]</span> <span class="{css}">{msg}</span></div>')
        render_log()

    novos, erros = 0, 0
    progress_bar = st.progress(0, text="Iniciando...")

    try:
        log("Conectando ao repositório MinIO...")
        from utils.minio_client import list_cv_files, download_file
        files = list_cv_files()
        log(f"Encontrados {len(files)} arquivo(s) no bucket.", "ok")

        log("Verificando planilha Google Sheets...")
        from utils.sheets import get_processed_files, append_cv, get_all_cvs
        processed = get_processed_files()
        log(f"{len(processed)} já processado(s) na planilha.", "dim")

        pending = [f for f in files if f["filename"] not in processed]
        log(f"{len(pending)} novo(s) currículo(s) para analisar.", "ok" if pending else "warn")

        if not pending:
            log("Nenhum currículo novo encontrado. Tudo atualizado!", "ok")
            progress_bar.progress(1.0, text="Concluído — sem novos currículos.")
        else:
            from utils.cv_parser import extract_text
            from utils.cv_analyzer import analyze_cv

            for idx, file in enumerate(pending, 1):
                fname = file["filename"]
                progress_bar.progress(idx / len(pending), text=f"Analisando {idx}/{len(pending)}: {fname}")
                try:
                    log(f"↓ Baixando: {fname}")
                    content = download_file(file["key"])

                    log(f"  Extraindo texto ({len(content)//1024} KB)...")
                    text = extract_text(content, fname)

                    log(f"  Analisando com IA...")
                    data = analyze_cv(text, fname)

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    append_cv(data, timestamp)
                    novos += 1
                    log(f"✓ {fname} — Nota: {data.get('nota', '?')} — {data.get('nome', '')}", "ok")
                except Exception as exc:
                    erros += 1
                    log(f"✗ Erro em {fname}: {exc}", "err")

            progress_bar.progress(1.0, text="Concluído!")
            log(f"Finalizado: {novos} novo(s) adicionado(s), {erros} erro(s).", "ok" if not erros else "warn")

        # Invalidate cached metrics
        _load_metrics.clear()

    except Exception as exc:
        log(f"Erro fatal: {exc}", "err")
        st.error(str(exc))
