import re
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

  /* Admin bar */
  .admin-bar {
    position: fixed; top: 0.55rem; left: 0.75rem;
    z-index: 9999; display: flex; gap: 5px;
  }
  .admin-link {
    background: rgba(255,255,255,0.5); color: #94A3B8 !important;
    font-size: 0.68rem; font-weight: 500; padding: 3px 9px;
    border-radius: 20px; border: 1px solid #E2E8F0;
    text-decoration: none !important; backdrop-filter: blur(4px);
    transition: all 0.18s; line-height: 1.6;
  }
  .admin-link:hover {
    background: rgba(255,255,255,0.92); color: #475569 !important;
    border-color: #CBD5E1;
  }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 65%, #3B82F6 100%);
    border-radius: 24px; padding: 3rem 2rem 2.5rem;
    margin: 2rem 0 1.8rem;
    box-shadow: 0 8px 40px rgba(37,99,235,0.28);
    text-align: center; position: relative; overflow: hidden;
  }
  .hero::before {
    content: ''; position: absolute;
    width: 300px; height: 300px; border-radius: 50%;
    background: rgba(255,255,255,0.05); top: -80px; right: -60px;
  }
  .hero span { font-size: 2.6rem; display: block; margin-bottom: 0.4rem; }
  .hero h1   { color: #fff; font-size: 1.9rem; font-weight: 800; margin: 0 0 0.4rem; }
  .hero p    { color: #BFDBFE; font-size: 0.92rem; margin: 0; line-height: 1.65; }

  /* Card genérico */
  .card {
    background: white; border-radius: 20px;
    padding: 2rem 1.8rem 1.8rem;
    box-shadow: 0 4px 24px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE; margin-bottom: 1.4rem;
  }
  .card-title { font-size: 1.05rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.25rem; text-align: center; }
  .card-desc  { font-size: 0.82rem; color: #64748B; text-align: center; margin-bottom: 1.4rem; }

  /* Input de telefone */
  .phone-wrapper {
    display: flex; align-items: stretch;
    border: 1.5px solid #DBEAFE; border-radius: 12px;
    overflow: hidden; background: #F8FAFC;
    margin-bottom: 1.2rem;
  }
  .phone-prefix {
    background: #EFF6FF; color: #1E3A8A;
    font-weight: 700; font-size: 0.95rem;
    padding: 0 14px; display: flex; align-items: center;
    white-space: nowrap; border-right: 1.5px solid #DBEAFE;
    gap: 6px;
  }
  /* Remove border do input dentro do wrapper */
  .phone-wrapper div[data-testid="stTextInput"] input {
    border: none !important; background: transparent !important;
    border-radius: 0 !important; font-size: 1rem !important;
  }
  .phone-wrapper div[data-testid="stTextInput"] > div {
    border: none !important; background: transparent !important;
  }

  /* Card de retorno (usuário existente) */
  .return-card {
    background: linear-gradient(135deg, #ECFDF5, #F0FDF4);
    border: 1.5px solid #6EE7B7; border-radius: 20px;
    padding: 1.8rem 2rem; margin-bottom: 1.2rem;
  }
  .return-greeting { font-size: 1.3rem; font-weight: 800; color: #065F46; margin-bottom: 0.3rem; }
  .return-subtitle { font-size: 0.85rem; color: #047857; margin-bottom: 1.2rem; }

  /* Dados do candidato (read-only) */
  .data-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0.7rem; margin-bottom: 1.2rem;
  }
  .data-item { background: white; border-radius: 10px; padding: 0.6rem 0.9rem; border: 1px solid #D1FAE5; }
  .data-label { font-size: 0.68rem; font-weight: 600; color: #059669; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
  .data-value { font-size: 0.88rem; color: #1E3A8A; font-weight: 500; word-break: break-word; }
  .data-item.full { grid-column: 1 / -1; }

  /* Card de revisão */
  .review-card {
    background: white; border-radius: 20px; padding: 2rem 2rem 1.5rem;
    box-shadow: 0 4px 24px rgba(37,99,235,0.09);
    border: 1.5px solid #93C5FD; margin-bottom: 1.4rem;
  }
  .review-title { font-size: 1.1rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.3rem; }
  .review-desc  { font-size: 0.83rem; color: #64748B; margin-bottom: 1.5rem; line-height: 1.5; }

  /* Agradecimento */
  .thank-you {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 1.5px solid #6EE7B7; border-radius: 20px;
    padding: 3rem 2rem; text-align: center; margin-bottom: 1.5rem;
  }
  .thank-you .ty-icon { font-size: 3.5rem; margin-bottom: 0.6rem; display: block; }
  .thank-you h2 { color: #065F46; font-size: 1.5rem; font-weight: 800; margin: 0 0 0.5rem; }
  .thank-you p  { color: #047857; font-size: 0.92rem; margin: 0; line-height: 1.7; }

  /* LGPD */
  .lgpd-box {
    background: #F0F9FF; border: 1px solid #BAE6FD;
    border-radius: 14px; padding: 16px 20px; margin: 1.4rem 0 0.6rem;
  }
  .lgpd-box-title { font-size: 0.87rem; font-weight: 700; color: #0369A1; margin-bottom: 6px; }
  .lgpd-box-text  { font-size: 0.81rem; color: #334155; line-height: 1.7; }
  .lgpd-link {
    display: inline-block; position: relative;
    color: #2563EB; font-weight: 600; cursor: pointer;
    text-decoration: underline dotted #93C5FD;
  }
  .lgpd-popup {
    display: none;
    position: absolute; bottom: 130%; left: -10px;
    width: 360px; background: white;
    border: 1px solid #BFDBFE; border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 8px 32px rgba(37,99,235,0.18);
    z-index: 9999; font-size: 0.76rem; color: #374151;
    line-height: 1.65; text-align: left; font-weight: 400;
  }
  .lgpd-popup::after {
    content: ''; position: absolute; top: 100%; left: 24px;
    border: 7px solid transparent; border-top-color: white;
  }
  .lgpd-link:hover .lgpd-popup { display: block; }

  /* Dialog de confirmação LGPD */
  .lgpd-dialog {
    background: #FFFBEB; border: 1.5px solid #FCD34D;
    border-radius: 16px; padding: 20px 22px; margin: 1rem 0;
  }
  .lgpd-dialog-icon { font-size: 1.8rem; margin-bottom: 6px; }
  .lgpd-dialog-title { font-size: 0.97rem; font-weight: 800; color: #92400E; margin-bottom: 6px; }
  .lgpd-dialog-text  { font-size: 0.84rem; color: #78350F; line-height: 1.65; }

  /* Botão primário */
  button[data-testid="stBaseButton-primary"],
  div[data-testid="stButton"] button[kind="primary"] {
    background: #2563EB !important; background-image: none !important;
    color: #fff !important; border: none !important;
    border-radius: 14px !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.75rem 2rem !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.32) !important;
  }
  button[data-testid="stBaseButton-primary"]:hover { background: #1D4ED8 !important; }

  /* Botão secundário */
  button[data-testid="stBaseButton-secondary"],
  div[data-testid="stButton"] button[kind="secondary"] {
    background: #F8FAFC !important; background-image: none !important;
    color: #64748B !important; border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important; font-weight: 500 !important; font-size: 0.85rem !important;
  }

  /* Inputs */
  div[data-testid="stTextInput"] input,
  div[data-testid="stTextArea"] textarea {
    border-radius: 10px; border: 1.5px solid #DBEAFE;
    font-size: 0.9rem; background: #F8FAFC;
  }
  div[data-testid="stFileUploader"] label { display: none; }

  /* Download button */
  div[data-testid="stDownloadButton"] button {
    background: rgba(255,255,255,0.5) !important; background-image: none !important;
    color: #94A3B8 !important; font-size: 0.68rem !important;
    font-weight: 500 !important; padding: 3px 9px !important;
    border-radius: 20px !important; border: 1px solid #E2E8F0 !important;
    box-shadow: none !important; min-height: unset !important; line-height: 1.6 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Admin bar ─────────────────────────────────────────────────────────────────
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
# app_state: "phone" | "returning" | "upload" | "review" | "submitted"
for k, v in [("app_state","phone"), ("cv_data",{}), ("found_phone",""),
              ("is_update",False), ("submit_type","new")]:
    if k not in st.session_state:
        st.session_state[k] = v

def _split_cidade_estado(value: str) -> tuple[str, str]:
    """Separa 'São Paulo, SP' em ('São Paulo', 'SP')."""
    if not value:
        return "", ""
    for sep in [", ", " - ", " / ", "/", ","]:
        if sep in value:
            parts = value.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return value.strip(), ""


def _fmt_phone(raw: str) -> str:
    """Formata dígitos como +55 (DD) NNNNN-NNNN."""
    d = re.sub(r"\D", "", raw)
    if d.startswith("55") and len(d) > 11:
        d = d[2:]
    if len(d) == 11:
        return f"+55 ({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"+55 ({d[:2]}) {d[2:6]}-{d[6:]}"
    return f"+55 {d}"


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: submitted
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "submitted":
    if st.session_state["submit_type"] == "returning":
        msg = """
        <div class="thank-you">
          <span class="ty-icon">👋</span>
          <h2>Tudo certo!</h2>
          <p>Seus dados estão atualizados em nossa base.<br>
             Entraremos em contato em breve se houver uma oportunidade para você.</p>
        </div>"""
    else:
        msg = """
        <div class="thank-you">
          <span class="ty-icon">✅</span>
          <h2>Currículo recebido!</h2>
          <p>Muito obrigado pelo seu interesse.<br>
             Nossa equipe irá analisar seu perfil e, se houver compatibilidade,<br>
             entraremos em contato em breve.</p>
        </div>"""
    st.markdown(msg, unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("📤  Novo envio", use_container_width=True, type="primary"):
            for k, v in [("app_state","phone"),("cv_data",{}),("found_phone",""),
                         ("is_update",False),("submit_type","new")]:
                st.session_state[k] = v
            st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: returning — usuário já cadastrado
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "returning":
    from utils.database import log_access
    d    = st.session_state["cv_data"]
    nome = d.get("nome") or "candidato"

    st.markdown(f"""
    <div class="return-card">
      <div class="return-greeting">Olá, {nome}! 👋</div>
      <div class="return-subtitle">
        Encontramos seu cadastro. Confira se seus dados estão corretos e clique em <strong>Avançar</strong>.
      </div>
      <div class="data-grid">
        <div class="data-item">
          <div class="data-label">📧 E-mail</div>
          <div class="data-value">{d.get('email') or '—'}</div>
        </div>
        <div class="data-item">
          <div class="data-label">📱 Telefone</div>
          <div class="data-value">{d.get('telefone') or '—'}</div>
        </div>
        <div class="data-item">
          <div class="data-label">📍 Cidade / Estado</div>
          <div class="data-value">{d.get('cidade_estado') or '—'}</div>
        </div>
        <div class="data-item">
          <div class="data-label">🌐 Idiomas</div>
          <div class="data-value">{d.get('idiomas') or '—'}</div>
        </div>
        <div class="data-item full">
          <div class="data-label">🎓 Formação</div>
          <div class="data-value">{d.get('formacao') or '—'}</div>
        </div>
        <div class="data-item full">
          <div class="data-label">💼 Experiência</div>
          <div class="data-value">{d.get('experiencia') or '—'}</div>
        </div>
        <div class="data-item full">
          <div class="data-label">🛠️ Habilidades</div>
          <div class="data-value">{d.get('habilidades') or '—'}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_av, col_at = st.columns(2)
    with col_av:
        if st.button("✅  Avançar", use_container_width=True, type="primary"):
            log_access(st.session_state["found_phone"], nome, "confirmou_dados")
            st.session_state["submit_type"] = "returning"
            st.session_state["app_state"]   = "submitted"
            st.rerun()
    with col_at:
        if st.button("🔄  Atualizar Currículo", use_container_width=True):
            log_access(st.session_state["found_phone"], nome, "iniciou_atualizacao")
            st.session_state["is_update"]  = True
            st.session_state["app_state"]  = "upload"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Voltar", type="secondary"):
        st.session_state["app_state"] = "phone"
        st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: review — revisão dos dados extraídos pelo candidato
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "review":
    from utils.database import get_processed_files, batch_insert_cvs, update_cv_by_phone, log_access
    d = st.session_state["cv_data"]

    # Inicializa campos no session_state quando entrar em review com novo CV
    if st.session_state.get("_rev_arquivo") != d.get("arquivo", ""):
        st.session_state["_rev_arquivo"]  = d.get("arquivo", "")
        st.session_state["rev_nome"]      = d.get("nome", "")
        st.session_state["rev_email"]     = d.get("email", "")
        st.session_state["rev_telefone"]  = d.get("telefone", "") or st.session_state.get("found_phone", "")
        _cidade, _estado = _split_cidade_estado(
            d.get("cidade_estado", "") or
            ", ".join(filter(None, [d.get("cidade",""), d.get("estado","")]))
        )
        st.session_state["rev_cidade"]    = _cidade
        st.session_state["rev_estado"]    = _estado
        st.session_state["rev_idiomas"]   = d.get("idiomas", "")
        st.session_state["rev_formacao"]  = d.get("formacao", "")
        st.session_state["rev_exp"]       = d.get("experiencia", "")
        st.session_state["rev_skills"]    = d.get("habilidades", "")
        st.session_state.pop("lgpd_aceito", None)
        st.session_state.pop("_lgpd_dialog", None)

    # ── Helper de salvamento ────────────────────────────────────────────────
    def _do_save(lgpd_value: str):
        d_final = {
            **d,
            "nome":          st.session_state["rev_nome"].strip(),
            "email":         st.session_state["rev_email"].strip(),
            "telefone":      st.session_state["rev_telefone"].strip(),
            "cidade_estado": ", ".join(filter(None, [
                                 st.session_state["rev_cidade"].strip(),
                                 st.session_state["rev_estado"].strip().upper(),
                             ])),
            "formacao":      st.session_state["rev_formacao"].strip(),
            "experiencia":   st.session_state["rev_exp"].strip(),
            "habilidades":   st.session_state["rev_skills"].strip(),
            "idiomas":       st.session_state["rev_idiomas"].strip(),
            "lgpd":          lgpd_value,
        }
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            if st.session_state["is_update"]:
                update_cv_by_phone(st.session_state["found_phone"], d_final, ts)
                log_access(d_final["telefone"], d_final["nome"], "atualizou_curriculo")
            else:
                processed = get_processed_files()
                if d_final.get("arquivo") not in processed:
                    batch_insert_cvs([(d_final, ts)])
                log_access(d_final["telefone"], d_final["nome"], "enviou_curriculo")

            acao_lgpd = "aceite_lgpd" if lgpd_value == "sim" else "recusou_lgpd"
            log_access(d_final["telefone"], d_final["nome"], acao_lgpd)

            _csv_data.clear()
            st.session_state.pop("lgpd_aceito", None)
            st.session_state.pop("_lgpd_dialog", None)
            st.session_state["submit_type"] = "update" if st.session_state["is_update"] else "new"
            st.session_state["app_state"]   = "submitted"
            st.session_state["cv_data"]     = {}
            st.rerun()
        except Exception as exc:
            st.error(f"Erro ao salvar os dados: {exc}")

    st.markdown("""
    <div class="review-card">
      <div class="review-title">🔍 Confirme seus dados</div>
      <p class="review-desc">
        Extraímos as informações abaixo do seu currículo automaticamente.<br>
        <strong>Revise, corrija se necessário</strong> e confirme para concluir o envio.
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        nome     = st.text_input("👤 Nome completo",  key="rev_nome")
        email    = st.text_input("📧 E-mail",          key="rev_email")
        telefone = st.text_input("📱 Telefone",        key="rev_telefone")
        cidade   = st.text_input("📍 Cidade",          key="rev_cidade")
        col_est, col_idi = st.columns([1, 2])
        with col_est:
            estado  = st.text_input("🗺️ Estado (UF)", key="rev_estado", max_chars=2)
        with col_idi:
            idiomas = st.text_input("🌐 Idiomas",     key="rev_idiomas")
    with col2:
        formacao = st.text_area("🎓 Formação acadêmica",       key="rev_formacao", height=110)
        exp      = st.text_area("💼 Experiência profissional",  key="rev_exp",      height=110)
        skills   = st.text_area("🛠️ Habilidades",               key="rev_skills",   height=110)

    # ── LGPD ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="lgpd-box">
      <div class="lgpd-box-title">🔒 Proteção de Dados — LGPD</div>
      <div class="lgpd-box-text">
        Seus dados serão usados <strong>exclusivamente para fins de recrutamento e seleção</strong>,
        conforme a nossa
        <span class="lgpd-link">Política de Privacidade
          <div class="lgpd-popup">
            <strong>📋 Política de Privacidade — StrategisTA</strong><br><br>
            <strong>Dados coletados:</strong> nome, e-mail, telefone, localização,
            formação, experiência, habilidades e idiomas.<br><br>
            <strong>Finalidade:</strong> identificação e contato em processos seletivos.<br><br>
            <strong>Base legal:</strong> consentimento do titular
            (Art. 7º, I — Lei nº 13.709/2018).<br><br>
            <strong>Retenção:</strong> até 2 anos ou até solicitação de exclusão.<br><br>
            <strong>Seus direitos:</strong> acesso, correção, exclusão e portabilidade
            dos dados (Art. 18 — LGPD).<br><br>
            <strong>Compartilhamento:</strong> seus dados <u>não serão vendidos</u>
            nem repassados a terceiros sem sua autorização.<br><br>
            <strong>Contato DPO:</strong> privacidade@strategista.com.br
          </div>
        </span>
        e nos termos da Lei nº 13.709/2018 (LGPD).
      </div>
    </div>
    """, unsafe_allow_html=True)

    lgpd_aceito = st.checkbox(
        "Li e concordo com o tratamento dos meus dados pessoais conforme a Política de Privacidade acima",
        key="lgpd_aceito",
    )

    st.markdown("<hr style='border:none;border-top:1.5px solid #DBEAFE;margin:1rem 0'>", unsafe_allow_html=True)

    # ── Dialog de confirmação LGPD (aparece quando clica sem marcar) ────────
    if st.session_state.get("_lgpd_dialog"):
        st.markdown("""
        <div class="lgpd-dialog">
          <div class="lgpd-dialog-icon">⚠️</div>
          <div class="lgpd-dialog-title">Confirmação de LGPD pendente</div>
          <div class="lgpd-dialog-text">
            Você não marcou o aceite da Política de Privacidade.<br>
            Gostaria de confirmar que <strong>aceita o tratamento dos seus dados pessoais</strong>
            conforme a LGPD (Lei nº 13.709/2018)?
          </div>
        </div>
        """, unsafe_allow_html=True)
        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("✅  Sim, aceito os termos", use_container_width=True,
                         type="primary", key="lgpd_sim_btn"):
                st.session_state.pop("_lgpd_dialog", None)
                _do_save("sim")
        with col_nao:
            if st.button("❌  Não, prosseguir sem aceitar", use_container_width=True,
                         key="lgpd_nao_btn"):
                st.session_state.pop("_lgpd_dialog", None)
                _do_save("não")

    col_confirm, col_back = st.columns([3, 1])
    with col_confirm:
        confirmar = st.button(
            "✅  Confirmo meus Dados",
            use_container_width=True,
            type="primary",
        )
    with col_back:
        voltar = st.button("← Voltar", use_container_width=True)

    if voltar:
        st.session_state.pop("lgpd_aceito", None)
        st.session_state.pop("_lgpd_dialog", None)
        prev = st.session_state.get("_review_origin", "phone")
        st.session_state["app_state"] = prev
        st.rerun()

    if confirmar:
        if lgpd_aceito:
            _do_save("sim")
        else:
            st.session_state["_lgpd_dialog"] = True
            st.rerun()

    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: upload — envio de arquivo
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state["app_state"] == "upload":
    titulo = "🔄 Atualize seu currículo" if st.session_state["is_update"] else "📎 Anexe seu currículo"
    desc   = "Envie a versão mais recente do seu CV (PDF ou DOCX)." if st.session_state["is_update"] \
             else "Formatos aceitos: PDF ou DOCX (Word)."

    st.markdown(f'<div class="card"><div class="card-title">{titulo}</div><div class="card-desc">{desc}</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CV", type=["pdf","docx"], accept_multiple_files=False, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        _, col_btn, _ = st.columns([1, 2, 1])
        with col_btn:
            enviar = st.button("📤  Enviar Currículo", use_container_width=True, type="primary")

        if st.session_state["is_update"]:
            if st.button("← Voltar", type="secondary"):
                st.session_state["app_state"] = "returning"
                st.rerun()

        if enviar:
            with st.spinner("Processando seu currículo..."):
                try:
                    from utils.cv_parser import extract_text
                    from utils.cv_analyzer import analyze_cv
                    content = uploaded_file.read()
                    text    = extract_text(content, uploaded_file.name)
                    data    = analyze_cv(text, uploaded_file.name)
                    # Preserva o telefone já informado
                    if not data.get("telefone") and st.session_state.get("found_phone"):
                        data["telefone"] = st.session_state["found_phone"]
                    st.session_state["cv_data"]        = data
                    st.session_state["_review_origin"] = "upload"
                    st.session_state["app_state"]      = "review"
                except Exception as exc:
                    st.error(f"Erro ao processar o arquivo: {exc}")
                    st.stop()
            st.rerun()
    else:
        if st.button("← Voltar", type="secondary"):
            st.session_state["app_state"] = "phone"
            st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO: phone — tela inicial com input de telefone
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📱 Informe seu telefone</div>', unsafe_allow_html=True)
st.markdown('<div class="card-desc">Seu número será usado para identificar seu cadastro.</div>', unsafe_allow_html=True)

# Input de telefone com prefixo 🇧🇷 +55
st.markdown('<div class="phone-wrapper">', unsafe_allow_html=True)
col_prefix, col_number = st.columns([1.1, 4])
with col_prefix:
    st.markdown('<div class="phone-prefix">🇧🇷 +55</div>', unsafe_allow_html=True)
with col_number:
    phone_raw = st.text_input(
        "Telefone", placeholder="11 99999-9999",
        label_visibility="collapsed",
        max_chars=15,
        key="phone_input",
    )
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if phone_raw and phone_raw.strip():
    digits = re.sub(r"\D", "", phone_raw)
    phone_ok = len(digits) >= 10

    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        avancar = st.button(
            "Avançar →",
            use_container_width=True,
            type="primary",
            disabled=not phone_ok,
        )

    if not phone_ok:
        st.caption("⚠️ Informe DDD + número (mínimo 10 dígitos).")

    if avancar and phone_ok:
        from utils.database import get_cv_by_phone, log_access
        phone_fmt = _fmt_phone(digits)

        with st.spinner("Verificando cadastro..."):
            existing = get_cv_by_phone(digits)

        if existing:
            nome_existente = existing.get("nome") or "candidato"
            log_access(phone_fmt, nome_existente, "acessou_sistema")
            st.session_state["cv_data"]       = existing
            st.session_state["found_phone"]   = phone_fmt
            st.session_state["is_update"]     = True
            st.session_state["_review_origin"] = "phone"
            st.session_state["app_state"]     = "review"
        else:
            log_access(phone_fmt, "", "novo_acesso")
            st.session_state["found_phone"] = phone_fmt
            st.session_state["app_state"]   = "upload"

        st.rerun()
