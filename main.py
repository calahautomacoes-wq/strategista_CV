import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Número de CVs processados em paralelo.
# 4 é seguro dentro do rate-limit da API Anthropic (~50 req/min).
_MAX_WORKERS = 4

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

  /* Primary buttons — solid blue */
  button[data-testid="stBaseButton-primary"],
  div[data-testid="stButton"] button[kind="primary"] {
    background: #2563EB !important;
    background-image: none !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 1.5rem !important;
    transition: background 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
  }
  button[data-testid="stBaseButton-primary"]:hover,
  div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 6px 18px rgba(37,99,235,0.45) !important;
  }

  /* Cancel / danger secondary button (único botão secundário desta página) */
  button[data-testid="stBaseButton-secondary"],
  div[data-testid="stButton"] button[kind="secondary"] {
    background: #FEF2F2 !important;
    background-image: none !important;
    color: #B91C1C !important;
    border: 1.5px solid #FECACA !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.4rem !important;
    transition: background 0.2s ease !important;
  }
  button[data-testid="stBaseButton-secondary"]:hover,
  div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #FEE2E2 !important;
    border-color: #F87171 !important;
    color: #991B1B !important;
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
        from utils.database import get_all_cvs
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
col_btn, col_btn2, col_info = st.columns([1, 1, 2], gap="large")

with col_btn:
    st.markdown("""<div class="action-card">
        <div class="action-title">Buscar novos currículos</div>
        <div class="action-desc">Verifica o repositório MinIO e processa apenas os arquivos ainda não analisados.</div>
    </div>""", unsafe_allow_html=True)
    buscar = st.button("🔍  Buscar CV", use_container_width=True, type="primary")

with col_btn2:
    st.markdown("""<div class="action-card">
        <div class="action-title">Visualizar currículos</div>
        <div class="action-desc">Consulte os currículos já analisados com detalhes completos e ranking.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("📄  Visualizar CV", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Curriculos.py")

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

    # Cancelar flag
    if "cancelar" not in st.session_state:
        st.session_state.cancelar = False
    st.session_state.cancelar = False

    log_lines: list[str] = []
    log_placeholder = st.empty()
    cancel_placeholder = st.empty()

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

    # Botão Cancelar — visível durante o processamento
    with cancel_placeholder.container():
        if st.button("⛔ Cancelar análise", key="cancelar_btn", type="secondary"):
            st.session_state.cancelar = True

    try:
        # ── 1. Listar arquivos e procesados em paralelo ────────────────────────
        log("Conectando ao repositório MinIO e Supabase...")
        from utils.minio_client import list_cv_files, download_file
        from utils.database import get_processed_files, batch_insert_cvs
        from utils.cv_parser import extract_text
        from utils.cv_analyzer import analyze_cv

        with ThreadPoolExecutor(max_workers=2) as init_exec:
            f_files     = init_exec.submit(list_cv_files)
            f_processed = init_exec.submit(get_processed_files)
            files     = f_files.result()
            processed = f_processed.result()

        log(f"Encontrados {len(files)} arquivo(s) no bucket.", "ok")
        log(f"{len(processed)} já processado(s) no banco.", "dim")

        pending = [f for f in files if f["filename"] not in processed]
        log(f"{len(pending)} novo(s) currículo(s) para analisar.", "ok" if pending else "warn")

        if not pending:
            log("Nenhum currículo novo encontrado. Tudo atualizado!", "ok")
            progress_bar.progress(1.0, text="Concluído — sem novos currículos.")
        else:
            # ── 2. Função worker (roda em threads) ────────────────────────────
            def _process_one(file_info: dict) -> tuple[str, dict]:
                """Download + extração + análise IA de um CV."""
                fname   = file_info["filename"]
                content = download_file(file_info["key"])
                text    = extract_text(content, fname)
                data    = analyze_cv(text, fname)
                return fname, data

            # ── 3. Processamento paralelo com batch insert ────────────────────
            _BATCH_SIZE = 10      # Insere no banco a cada N CVs concluídos
            batch_buffer: list[tuple[dict, str]] = []
            done_count = 0

            with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
                future_map = {executor.submit(_process_one, f): f for f in pending}

                for future in as_completed(future_map):
                    done_count += 1
                    file_info = future_map[future]
                    fname     = file_info["filename"]
                    short     = fname[:45] + "…" if len(fname) > 45 else fname
                    progress_bar.progress(
                        done_count / len(pending),
                        text=f"Analisando {done_count}/{len(pending)}: {short}",
                    )

                    # Verificar cancelamento (entre futures, não dentro do worker)
                    if st.session_state.get("cancelar"):
                        for f in future_map:
                            f.cancel()
                        log(f"⛔ Análise cancelada após {novos} CV(s) processado(s).", "warn")
                        progress_bar.progress(done_count / len(pending), text="Cancelado.")
                        break

                    try:
                        _, data = future.result()
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                        batch_buffer.append((data, ts))
                        novos += 1
                        log(f"✓ {fname} — Nota: {data.get('nota', '?')} — {data.get('nome', '')}", "ok")
                    except Exception as exc:
                        erros += 1
                        log(f"✗ Erro em {fname}: {exc}", "err")

                    # Flush batch quando atingir o tamanho limite
                    if len(batch_buffer) >= _BATCH_SIZE:
                        try:
                            batch_insert_cvs(batch_buffer)
                            batch_buffer.clear()
                        except Exception as exc:
                            log(f"✗ Erro ao salvar lote no banco: {exc}", "err")

                # Inserir registros restantes
                if batch_buffer:
                    try:
                        batch_insert_cvs(batch_buffer)
                    except Exception as exc:
                        log(f"✗ Erro ao salvar registros finais: {exc}", "err")

            if not st.session_state.get("cancelar"):
                progress_bar.progress(1.0, text="Concluído!")
                log(f"Finalizado: {novos} novo(s) adicionado(s), {erros} erro(s).",
                    "ok" if not erros else "warn")

        # Remover botão cancelar e atualizar métricas
        cancel_placeholder.empty()
        _load_metrics.clear()

    except Exception as exc:
        cancel_placeholder.empty()
        log(f"Erro fatal: {exc}", "err")
        st.error(str(exc))
