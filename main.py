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

  /* Cancel / danger secondary button */
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

  /* Upload area */
  .upload-panel {
    background: white;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.09);
    border: 1.5px dashed #93C5FD;
    margin-top: 1rem;
  }
  .upload-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.4rem;
  }
  .upload-desc {
    font-size: 0.82rem;
    color: #64748B;
    margin-bottom: 1rem;
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

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">StrategisTA</div>
  <h1>📋 Análise de Currículos</h1>
  <p>Envie currículos em PDF ou DOCX e receba análise completa com IA — em segundos.</p>
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
        <div class="action-title">Enviar currículo</div>
        <div class="action-desc">Envie um ou mais arquivos PDF ou DOCX para análise automática com IA.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("📤  Enviar CV", use_container_width=True, type="primary"):
        st.session_state["show_uploader"] = not st.session_state.get("show_uploader", False)

with col_btn2:
    st.markdown("""<div class="action-card">
        <div class="action-title">Visualizar currículos</div>
        <div class="action-desc">Consulte os currículos já analisados com detalhes completos e ranking.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("📄  Visualizar CV", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Curriculos.py")

with col_info:
    if _missing_setup:
        st.warning("**Configuração pendente:**")
        for item in _missing_setup:
            st.markdown(f"- {item}")
    else:
        st.info("Sistema configurado. Clique em **Enviar CV** para fazer upload e analisar currículos. Arquivos já processados serão ignorados automaticamente.")

# ── Upload panel ───────────────────────────────────────────────────────────────
if st.session_state.get("show_uploader"):
    st.markdown('<div class="section-title">Upload de Currículos</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
        st.markdown('<div class="upload-title">📎 Selecione os arquivos</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-desc">Formatos aceitos: PDF e DOCX. Você pode enviar vários arquivos de uma vez.</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Currículos",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_files:
        col_proc, col_cancel = st.columns([1, 5])
        with col_proc:
            analisar = st.button(
                f"🔍  Analisar {len(uploaded_files)} CV(s)",
                type="primary",
                use_container_width=True,
            )
        with col_cancel:
            if st.button("✕  Fechar", type="secondary"):
                st.session_state["show_uploader"] = False
                st.rerun()
    else:
        analisar = False
        if st.button("✕  Fechar upload", type="secondary"):
            st.session_state["show_uploader"] = False
            st.rerun()

    # ── Processing ────────────────────────────────────────────────────────────
    if uploaded_files and analisar:
        if _missing_setup:
            st.error("Corrija os itens de configuração acima antes de continuar.")
            st.stop()

        st.session_state["cancelar"] = False

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

        with cancel_placeholder.container():
            if st.button("⛔ Cancelar análise", key="cancelar_btn", type="secondary"):
                st.session_state["cancelar"] = True

        try:
            from utils.database import get_processed_files, batch_insert_cvs
            from utils.cv_parser import extract_text
            from utils.cv_analyzer import analyze_cv

            log("Verificando arquivos já processados no banco...")
            processed = get_processed_files()
            log(f"{len(processed)} arquivo(s) já registrado(s) no banco.", "dim")

            # Filtrar duplicados
            pending = [f for f in uploaded_files if f.name not in processed]
            skipped = len(uploaded_files) - len(pending)
            if skipped:
                log(f"{skipped} arquivo(s) ignorado(s) — já analisados anteriormente.", "warn")
            log(f"{len(pending)} novo(s) currículo(s) para analisar.", "ok" if pending else "warn")

            if not pending:
                log("Todos os arquivos enviados já foram analisados anteriormente.", "warn")
                progress_bar.progress(1.0, text="Nenhum arquivo novo.")
            else:
                # Worker: extrai texto e analisa um CV
                def _process_one(uploaded_file) -> tuple[str, dict]:
                    content = uploaded_file.read()
                    text    = extract_text(content, uploaded_file.name)
                    data    = analyze_cv(text, uploaded_file.name)
                    return uploaded_file.name, data

                _BATCH_SIZE = 10
                batch_buffer: list[tuple[dict, str]] = []
                done_count = 0

                with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
                    future_map = {executor.submit(_process_one, f): f for f in pending}

                    for future in as_completed(future_map):
                        done_count += 1
                        uf    = future_map[future]
                        fname = uf.name
                        short = fname[:45] + "…" if len(fname) > 45 else fname
                        progress_bar.progress(
                            done_count / len(pending),
                            text=f"Analisando {done_count}/{len(pending)}: {short}",
                        )

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

                        if len(batch_buffer) >= _BATCH_SIZE:
                            try:
                                batch_insert_cvs(batch_buffer)
                                batch_buffer.clear()
                            except Exception as exc:
                                log(f"✗ Erro ao salvar lote no banco: {exc}", "err")

                    if batch_buffer:
                        try:
                            batch_insert_cvs(batch_buffer)
                        except Exception as exc:
                            log(f"✗ Erro ao salvar registros finais: {exc}", "err")

                if not st.session_state.get("cancelar"):
                    progress_bar.progress(1.0, text="Concluído!")
                    log(f"Finalizado: {novos} novo(s) adicionado(s), {erros} erro(s).",
                        "ok" if not erros else "warn")

        except Exception as exc:
            log(f"Erro fatal: {exc}", "err")
            st.error(str(exc))
        finally:
            cancel_placeholder.empty()
            _load_metrics.clear()
