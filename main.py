import time
import streamlit as st
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

_MAX_WORKERS = 4

st.set_page_config(
    page_title="StrategisTA",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .stApp { background: #EFF6FF; }

  /* Barra admin discreta — canto superior esquerdo */
  .admin-bar {
    position: fixed;
    top: 0.55rem;
    left: 0.75rem;
    z-index: 9999;
    display: flex;
    gap: 5px;
  }
  .admin-link {
    background: rgba(255,255,255,0.5);
    color: #94A3B8 !important;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    text-decoration: none !important;
    backdrop-filter: blur(4px);
    transition: all 0.18s;
    line-height: 1.6;
  }
  .admin-link:hover {
    background: rgba(255,255,255,0.92);
    color: #475569 !important;
    border-color: #CBD5E1;
  }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 65%, #3B82F6 100%);
    border-radius: 24px;
    padding: 3.5rem 2rem 3rem;
    margin: 2rem 0 2rem;
    box-shadow: 0 8px 40px rgba(37,99,235,0.28);
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    width: 300px; height: 300px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
    top: -80px; right: -60px;
  }
  .hero::after {
    content: '';
    position: absolute;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
    bottom: -50px; left: -30px;
  }
  .hero span { font-size: 2.8rem; display: block; margin-bottom: 0.4rem; }
  .hero h1 {
    color: #fff; font-size: 2rem; font-weight: 800;
    margin: 0 0 0.5rem; letter-spacing: -0.5px;
  }
  .hero p { color: #BFDBFE; font-size: 0.95rem; margin: 0; line-height: 1.65; }

  /* Card upload */
  .upload-card {
    background: white;
    border-radius: 20px;
    padding: 2.2rem 1.8rem 1.8rem;
    box-shadow: 0 4px 24px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE;
    margin-bottom: 1.5rem;
  }
  .upload-card-title {
    font-size: 1.05rem; font-weight: 700; color: #1E3A8A;
    margin-bottom: 0.25rem; text-align: center;
  }
  .upload-card-desc {
    font-size: 0.82rem; color: #64748B;
    text-align: center; margin-bottom: 1.4rem;
  }

  /* Botão principal */
  button[data-testid="stBaseButton-primary"],
  div[data-testid="stButton"] button[kind="primary"] {
    background: #2563EB !important;
    background-image: none !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.32) !important;
    transition: background 0.2s !important;
  }
  button[data-testid="stBaseButton-primary"]:hover {
    background: #1D4ED8 !important;
  }

  /* Botão secundário */
  button[data-testid="stBaseButton-secondary"],
  div[data-testid="stButton"] button[kind="secondary"] {
    background: #F8FAFC !important;
    background-image: none !important;
    color: #64748B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
  }

  /* Agradecimento */
  .thank-you {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 1.5px solid #6EE7B7;
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
  }
  .thank-you .ty-icon { font-size: 3.5rem; margin-bottom: 0.6rem; display: block; }
  .thank-you h2 { color: #065F46; font-size: 1.5rem; font-weight: 800; margin: 0 0 0.5rem; }
  .thank-you p  { color: #047857; font-size: 0.92rem; margin: 0; line-height: 1.7; }

  /* Esconde label do file uploader */
  div[data-testid="stFileUploader"] label { display: none; }

  /* Download button (admin csv) — estilo link discreto */
  div[data-testid="stDownloadButton"] button {
    background: rgba(255,255,255,0.5) !important;
    background-image: none !important;
    color: #94A3B8 !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    padding: 3px 9px !important;
    border-radius: 20px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: none !important;
    min-height: unset !important;
    line-height: 1.6 !important;
  }
  div[data-testid="stDownloadButton"] button:hover {
    background: rgba(255,255,255,0.92) !important;
    color: #475569 !important;
    border-color: #CBD5E1 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Barra admin discreta ──────────────────────────────────────────────────────
st.markdown("""
<div class="admin-bar">
  <a class="admin-link" href="/Curriculos" target="_self">📄 Ver CVs</a>
</div>
""", unsafe_allow_html=True)

# Botão CSV — carrega dados só se necessário (cache 5 min)
@st.cache_data(ttl=300)
def _csv_data():
    try:
        import pandas as pd
        from utils.database import get_all_cvs
        df = get_all_cvs()
        return df.to_csv(index=False).encode("utf-8") if not df.empty else None
    except Exception:
        return None

_csv = _csv_data()
if _csv:
    # Pequeno download button alinhado ao lado do "Ver CVs"
    # Streamlit não permite posicionamento fixo para widgets nativos,
    # então usamos um container minúsculo no topo
    _spacer, _dl_col = st.columns([20, 1])
    with _dl_col:
        st.download_button(
            "⬇️",
            data=_csv,
            file_name="curriculos_strategista.csv",
            mime="text/csv",
            help="Baixar CSV com todos os currículos",
            key="csv_dl_top",
        )


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span>📋</span>
  <h1>Envie seu Currículo</h1>
  <p>Estamos sempre em busca de talentos.<br>
     Envie seu currículo e nossa equipe entrará em contato.</p>
</div>
""", unsafe_allow_html=True)


# ── Tela de agradecimento ─────────────────────────────────────────────────────
if st.session_state.get("submitted"):
    st.markdown("""
    <div class="thank-you">
      <span class="ty-icon">✅</span>
      <h2>Recebemos seu currículo!</h2>
      <p>Muito obrigado pelo seu interesse.<br>
         Nossa equipe irá analisar seu perfil e, se houver compatibilidade,<br>
         entraremos em contato em breve.</p>
    </div>
    """, unsafe_allow_html=True)

    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("📤  Enviar outro currículo", use_container_width=True, type="primary"):
            st.session_state["submitted"] = False
            st.rerun()
    st.stop()


# ── Card de upload ────────────────────────────────────────────────────────────
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown('<div class="upload-card-title">📎 Anexe seu currículo</div>', unsafe_allow_html=True)
st.markdown('<div class="upload-card-desc">Formatos aceitos: PDF ou DOCX (Word)</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Currículo",
    type=["pdf", "docx"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        enviar = st.button("📤  Enviar Currículo", use_container_width=True, type="primary")

    if enviar:
        # ── Spinner "Enviando..." — cobre todo o processamento ────────────────
        sending_placeholder = st.empty()
        sending_placeholder.markdown("""
        <div style="
          background:#EFF6FF; border:1.5px solid #BFDBFE; border-radius:16px;
          padding:2rem; text-align:center; margin-top:1rem;
        ">
          <div style="font-size:2rem">⏳</div>
          <p style="color:#1E40AF; font-weight:600; margin:0.5rem 0 0; font-size:0.95rem">
            Enviando seu currículo…<br>
            <span style="font-weight:400; font-size:0.85rem">Aguarde um momento, por favor.</span>
          </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Processamento silencioso ──────────────────────────────────────────
        try:
            from utils.database import get_processed_files, batch_insert_cvs
            from utils.cv_parser import extract_text
            from utils.cv_analyzer import analyze_cv

            fname   = uploaded_file.name
            content = uploaded_file.read()

            # Só processa se não foi enviado antes
            processed = get_processed_files()
            if fname not in processed:
                text = extract_text(content, fname)
                data = analyze_cv(text, fname)
                ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
                batch_insert_cvs([(data, ts)])

            # Invalida cache do CSV para próxima vez
            _csv_data.clear()

        except Exception:
            pass  # Não exibe erros técnicos ao candidato

        sending_placeholder.empty()
        st.session_state["submitted"] = True
        st.rerun()
