import streamlit as st
from datetime import datetime
from pathlib import Path

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

  /* Barra admin discreta */
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
    padding: 3rem 2rem 2.5rem;
    margin: 2rem 0 1.8rem;
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
  .hero span { font-size: 2.6rem; display: block; margin-bottom: 0.4rem; }
  .hero h1 { color: #fff; font-size: 1.9rem; font-weight: 800; margin: 0 0 0.4rem; letter-spacing: -0.5px; }
  .hero p  { color: #BFDBFE; font-size: 0.92rem; margin: 0; line-height: 1.65; }

  /* Card genérico */
  .card {
    background: white;
    border-radius: 20px;
    padding: 2rem 1.8rem 1.8rem;
    box-shadow: 0 4px 24px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE;
    margin-bottom: 1.4rem;
  }
  .card-title {
    font-size: 1.05rem; font-weight: 700; color: #1E3A8A;
    margin-bottom: 0.25rem; text-align: center;
  }
  .card-desc {
    font-size: 0.82rem; color: #64748B;
    text-align: center; margin-bottom: 1.4rem;
  }

  /* Card de revisão */
  .review-card {
    background: white;
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    box-shadow: 0 4px 24px rgba(37,99,235,0.09);
    border: 1.5px solid #93C5FD;
    margin-bottom: 1.4rem;
  }
  .review-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 0.3rem;
  }
  .review-title { font-size: 1.1rem; font-weight: 800; color: #1E3A8A; }
  .review-desc  { font-size: 0.83rem; color: #64748B; margin-bottom: 1.5rem; line-height: 1.5; }
  .review-divider {
    border: none; border-top: 1.5px solid #DBEAFE;
    margin: 1.2rem 0 1.2rem;
  }

  /* Botão primário */
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
  button[data-testid="stBaseButton-primary"]:hover { background: #1D4ED8 !important; }

  /* Botão secundário */
  button[data-testid="stBaseButton-secondary"],
  div[data-testid="stButton"] button[kind="secondary"] {
    background: #F8FAFC !important;
    background-image: none !important;
    color: #64748B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
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

  /* Inputs do formulário */
  div[data-testid="stTextInput"] input,
  div[data-testid="stTextArea"] textarea {
    border-radius: 10px;
    border: 1.5px solid #DBEAFE;
    font-size: 0.9rem;
    background: #F8FAFC;
  }
  div[data-testid="stTextInput"] input:focus,
  div[data-testid="stTextArea"] textarea:focus {
    border-color: #2563EB;
    background: white;
  }
  div[data-testid="stFileUploader"] label { display: none; }

  /* Download button admin */
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
    _spacer, _dl_col = st.columns([20, 1])
    with _dl_col:
        st.download_button("⬇️", data=_csv, file_name="curriculos_strategista.csv",
                           mime="text/csv", help="Baixar CSV", key="csv_dl_top")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span>📋</span>
  <h1>Envie seu Currículo</h1>
  <p>Estamos sempre em busca de talentos.<br>
     Envie seu currículo e nossa equipe entrará em contato.</p>
</div>
""", unsafe_allow_html=True)

# ── Inicializar estados ───────────────────────────────────────────────────────
if "app_state" not in st.session_state:
    st.session_state["app_state"] = "upload"   # upload | review | submitted
if "cv_data" not in st.session_state:
    st.session_state["cv_data"] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: submitted — Tela de agradecimento
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "submitted":
    st.markdown("""
    <div class="thank-you">
      <span class="ty-icon">✅</span>
      <h2>Dados confirmados!</h2>
      <p>Seu currículo foi recebido com sucesso.<br>
         Nossa equipe irá analisar seu perfil e, se houver compatibilidade,<br>
         entraremos em contato em breve.</p>
    </div>
    """, unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("📤  Enviar outro currículo", use_container_width=True, type="primary"):
            st.session_state["app_state"] = "upload"
            st.session_state["cv_data"]   = {}
            st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: review — Revisão e edição dos dados extraídos
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "review":
    d = st.session_state["cv_data"]

    st.markdown("""
    <div class="review-card">
      <div class="review-header">
        <span style="font-size:1.5rem">🔍</span>
        <span class="review-title">Confirme seus dados</span>
      </div>
      <p class="review-desc">
        Extraímos as informações abaixo do seu currículo automaticamente.<br>
        <strong>Revise, corrija se necessário</strong> e confirme para concluir o envio.
      </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("review_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome     = st.text_input("👤 Nome completo",  value=d.get("nome", ""))
            email    = st.text_input("📧 E-mail",          value=d.get("email", ""))
            telefone = st.text_input("📱 Telefone",        value=d.get("telefone", ""))
            cidade   = st.text_input("📍 Cidade / Estado", value=d.get("cidade_estado", ""))
            idiomas  = st.text_input("🌐 Idiomas",         value=d.get("idiomas", ""))
        with col2:
            formacao = st.text_area("🎓 Formação acadêmica",      value=d.get("formacao", ""),    height=110)
            exp      = st.text_area("💼 Experiência profissional", value=d.get("experiencia", ""), height=110)
            skills   = st.text_area("🛠️ Habilidades",              value=d.get("habilidades", ""), height=110)

        st.markdown("<hr class='review-divider'>", unsafe_allow_html=True)

        col_confirm, col_back = st.columns([3, 1])
        with col_confirm:
            confirmar = st.form_submit_button(
                "✅  Confirmo meus Dados",
                use_container_width=True,
                type="primary",
            )
        with col_back:
            voltar = st.form_submit_button(
                "← Refazer envio",
                use_container_width=True,
            )

    if voltar:
        st.session_state["app_state"] = "upload"
        st.session_state["cv_data"]   = {}
        st.rerun()

    if confirmar:
        # Atualiza os dados com o que o candidato editou
        d_final = {
            **d,  # preserva nota, resumo, justificativa, arquivo
            "nome":          nome.strip(),
            "email":         email.strip(),
            "telefone":      telefone.strip(),
            "cidade_estado": cidade.strip(),
            "formacao":      formacao.strip(),
            "experiencia":   exp.strip(),
            "habilidades":   skills.strip(),
            "idiomas":       idiomas.strip(),
        }
        try:
            from utils.database import get_processed_files, batch_insert_cvs
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            processed = get_processed_files()
            if d_final.get("arquivo") not in processed:
                batch_insert_cvs([(d_final, ts)])
            _csv_data.clear()
            st.session_state["app_state"] = "submitted"
            st.session_state["cv_data"]   = {}
            st.rerun()
        except Exception as exc:
            st.error(f"Erro ao salvar os dados: {exc}")

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: upload — Formulário de envio de arquivo
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📎 Anexe seu currículo</div>', unsafe_allow_html=True)
st.markdown('<div class="card-desc">Formatos aceitos: PDF ou DOCX (Word)</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Currículo", type=["pdf", "docx"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        enviar = st.button("📤  Enviar Currículo", use_container_width=True, type="primary")

    if enviar:
        # Mostra spinner enquanto a IA extrai e analisa
        with st.spinner("Processando seu currículo..."):
            try:
                from utils.cv_parser import extract_text
                from utils.cv_analyzer import analyze_cv

                content = uploaded_file.read()
                text    = extract_text(content, uploaded_file.name)
                data    = analyze_cv(text, uploaded_file.name)

                st.session_state["cv_data"]   = data
                st.session_state["app_state"] = "review"

            except Exception as exc:
                st.error(f"Erro ao processar o arquivo: {exc}")
                st.stop()

        st.rerun()
