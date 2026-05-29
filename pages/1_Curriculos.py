import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Currículos · StrategisTA", page_icon="📄", layout="wide")

st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .stApp { background: #EFF6FF; }

  /* Page header */
  .page-header {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 65%, #3B82F6 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(37,99,235,0.25);
  }
  .page-header h2 { color: white; font-size: 1.6rem; font-weight: 800; margin: 0; }
  .page-header p  { color: #BFDBFE; margin: 0.2rem 0 0; font-size: 0.9rem; }

  /* CV list item */
  .cv-item {
    background: white;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    cursor: pointer;
    border: 2px solid transparent;
    box-shadow: 0 1px 8px rgba(37,99,235,0.07);
    transition: all 0.15s ease;
  }
  .cv-item:hover { border-color: #93C5FD; }
  .cv-item.selected { border-color: #2563EB; background: #EFF6FF; }
  .cv-item-name { font-weight: 700; color: #1E3A8A; font-size: 0.95rem; }
  .cv-item-meta { font-size: 0.75rem; color: #64748B; margin-top: 2px; }

  /* Score badge in list */
  .score-sm {
    display: inline-block;
    background: #1E40AF;
    color: white;
    font-weight: 800;
    font-size: 0.8rem;
    border-radius: 20px;
    padding: 2px 9px;
    float: right;
    margin-top: 2px;
  }
  .score-sm.high  { background: #059669; }
  .score-sm.mid   { background: #D97706; }
  .score-sm.low   { background: #DC2626; }

  /* Detail panel */
  .detail-panel {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.09);
    border: 1px solid #DBEAFE;
    min-height: 500px;
  }

  /* Score circle */
  .score-circle {
    width: 80px; height: 80px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; font-weight: 900;
    color: white;
    float: right;
    margin: 0 0 1rem 1rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  }

  /* Candidate header */
  .cand-name { font-size: 1.6rem; font-weight: 800; color: #1E3A8A; margin-bottom: 4px; }
  .cand-contact { font-size: 0.85rem; color: #64748B; margin-bottom: 1rem; }
  .cand-contact span { margin-right: 1.2rem; }

  /* Section titles */
  .sec-title {
    font-size: 0.7rem; font-weight: 700; color: #2563EB;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin: 1.2rem 0 0.4rem;
    padding-bottom: 4px;
    border-bottom: 1.5px solid #DBEAFE;
  }
  .sec-body { font-size: 0.9rem; color: #334155; line-height: 1.6; }

  /* Summary box */
  .summary-box {
    background: #EFF6FF;
    border-left: 3px solid #2563EB;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    font-size: 0.88rem;
    color: #1E3A8A;
    line-height: 1.6;
    margin: 0.5rem 0 0.5rem;
  }

  /* Justification box */
  .just-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    color: #475569;
    font-style: italic;
    margin-top: 0.3rem;
  }

  /* Empty state */
  .empty-state {
    text-align: center;
    color: #94A3B8;
    padding: 4rem 2rem;
  }
  .empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
  .empty-state p { font-size: 0.95rem; }

  /* Search box */
  div[data-testid="stTextInput"] input {
    border-radius: 10px;
    border: 1.5px solid #DBEAFE;
    font-size: 0.9rem;
  }

  /* Primary buttons */
  button[data-testid="stBaseButton-primary"],
  div[data-testid="stButton"] button[kind="primary"] {
    background: #2563EB !important;
    background-image: none !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.3) !important;
    transition: background 0.2s ease !important;
  }
  button[data-testid="stBaseButton-primary"]:hover,
  div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #1D4ED8 !important;
  }
  /* Secondary / default buttons */
  button[data-testid="stBaseButton-secondary"],
  div[data-testid="stButton"] button[kind="secondary"] {
    background: #ffffff !important;
    background-image: none !important;
    color: #475569 !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }
  button[data-testid="stBaseButton-secondary"]:hover,
  div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #F1F5F9 !important;
  }

  /* Tabs */
  div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 600;
    font-size: 0.9rem;
  }
  div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #2563EB;
    border-bottom-color: #2563EB;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📄 Currículos Analisados</h2>
  <p>Visualize detalhes dos candidatos ou consulte a tabela completa com todos os dados.</p>
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_latest():
    """Dados para exibição: um registro por candidato (mais recente)."""
    try:
        from utils.database import get_latest_cvs
        return get_latest_cvs()
    except Exception as exc:
        st.error(f"Erro ao carregar dados: {exc}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_all():
    """Histórico completo para exportação em CSV."""
    try:
        from utils.database import get_all_cvs
        return get_all_cvs()
    except Exception as exc:
        return pd.DataFrame()

df = load_latest()

if df is None or df.empty:
    st.info("Nenhum currículo analisado ainda. Vá à página inicial e clique em **Enviar CV** para fazer upload e analisar.")
    if st.button("← Voltar"):
        st.switch_page("main.py")
    st.stop()

# ── CSV Download (histórico completo) ─────────────────────────────────────────
df_all = load_all()
csv_bytes = (df_all if not df_all.empty else df).to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️  Baixar CSV (histórico completo)",
    data=csv_bytes,
    file_name="curriculos_strategista.csv",
    mime="text/csv",
    use_container_width=False,
)

# ── Abas ──────────────────────────────────────────────────────────────────────
tab_cards, tab_tabela, tab_ranking = st.tabs(["🗂️  Detalhes", "📋  Tabela Completa", "📊  Ranking"])

# ═══════════════════════════════════════════════════════════════════════════════
# ABA 1 — Cards + painel de detalhe
# ═══════════════════════════════════════════════════════════════════════════════
with tab_cards:
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = 0

    col_nav, col_detail = st.columns([1, 2], gap="large")

    # ── Esquerda: lista de candidatos ─────────────────────────────────────────
    with col_nav:
        search = st.text_input("🔍 Filtrar candidatos", placeholder="Nome, habilidade...")

        filtered = df.copy()
        if search:
            mask = filtered.apply(lambda r: search.lower() in r.to_string().lower(), axis=1)
            filtered = filtered[mask]

        filtered = filtered.sort_values("Nota", ascending=False).reset_index(drop=True)
        st.caption(f"{len(filtered)} candidato(s)")

        for i, row in filtered.iterrows():
            nota = row.get("Nota", 0)
            try:
                nota_f = float(nota)
            except (TypeError, ValueError):
                nota_f = 0.0

            score_cls = "high" if nota_f >= 8 else ("mid" if nota_f >= 6 else "low")
            nota_str  = f"{nota_f:.0f}"
            nome  = row.get("Nome") or row.get("Arquivo") or f"Candidato {i+1}"
            data  = row.get("Data de Análise", "")
            cidade = row.get("Cidade/Estado", "")
            sub   = " · ".join(filter(None, [cidade, data]))

            selected  = st.session_state.selected_idx == i
            card_cls  = "cv-item selected" if selected else "cv-item"

            st.markdown(f"""
            <div class="{card_cls}">
              <span class="score-sm {score_cls}">{nota_str}</span>
              <div class="cv-item-name">{nome}</div>
              <div class="cv-item-meta">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver detalhes", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_idx = i
                st.rerun()

    # ── Direita: painel de detalhe ────────────────────────────────────────────
    with col_detail:
        if filtered.empty:
            st.markdown("""<div class="detail-panel">
              <div class="empty-state">
                <div class="icon">🔍</div>
                <p>Nenhum candidato encontrado com esse filtro.</p>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            idx = min(st.session_state.selected_idx, len(filtered) - 1)
            row = filtered.iloc[idx]

            nota = row.get("Nota", 0)
            try:
                nota_f = float(nota)
            except (TypeError, ValueError):
                nota_f = 0.0

            score_color = "#059669" if nota_f >= 8 else ("#D97706" if nota_f >= 6 else "#DC2626")
            nota_str = f"{nota_f:.0f}"

            nome     = row.get("Nome") or "—"
            email    = row.get("Email") or "—"
            telefone = row.get("Telefone") or "—"
            cidade   = row.get("Cidade/Estado") or "—"
            formacao = row.get("Formação") or "—"
            exp      = row.get("Experiência") or "—"
            skills   = row.get("Habilidades") or "—"
            idiomas  = row.get("Idiomas") or "—"
            resumo   = row.get("Resumo") or "—"
            just     = row.get("Justificativa") or "—"
            arquivo  = row.get("Arquivo") or "—"
            data_ana = row.get("Data de Análise") or "—"

            st.markdown(f"""
            <div class="detail-panel">
              <div class="score-circle" style="background:{score_color}">{nota_str}</div>
              <div class="cand-name">{nome}</div>
              <div class="cand-contact">
                <span>📧 {email}</span>
                <span>📱 {telefone}</span>
                <span>📍 {cidade}</span>
              </div>
              <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:1rem;">
                Arquivo: {arquivo} &nbsp;·&nbsp; Analisado em: {data_ana}
              </div>
              <div class="sec-title">Resumo Profissional</div>
              <div class="summary-box">{resumo}</div>
              <div class="sec-title">Formação Acadêmica</div>
              <div class="sec-body">{formacao}</div>
              <div class="sec-title">Experiência Profissional</div>
              <div class="sec-body">{exp}</div>
              <div class="sec-title">Habilidades</div>
              <div class="sec-body">{skills}</div>
              <div class="sec-title">Idiomas</div>
              <div class="sec-body">{idiomas}</div>
              <div class="sec-title">Justificativa da Nota</div>
              <div class="just-box">{just}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ABA 2 — Tabela completa com Resumo
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tabela:
    st.markdown("#### Todos os candidatos")

    # Busca/filtro
    busca_tab = st.text_input("🔍 Filtrar", placeholder="Nome, habilidade, cidade...", key="busca_tab")
    df_tab = df.copy()
    if busca_tab:
        mask = df_tab.apply(lambda r: busca_tab.lower() in r.to_string().lower(), axis=1)
        df_tab = df_tab[mask]

    df_tab = df_tab.sort_values("Nota", ascending=False).reset_index(drop=True)

    # Colunas e ordem para exibição na tabela
    colunas_tabela = [
        "Nome", "Sexo", "Nota", "Resumo", "Cidade/Estado",
        "Formação", "Experiência", "Habilidades",
        "Idiomas", "Email", "Telefone",
        "Justificativa", "Data de Análise", "Arquivo",
    ]
    colunas_existentes = [c for c in colunas_tabela if c in df_tab.columns]
    df_view = df_tab[colunas_existentes]

    st.dataframe(
        df_view,
        use_container_width=True,
        height=560,
        column_config={
            "Nota": st.column_config.NumberColumn(
                "Nota",
                format="%.0f ⭐",
                min_value=0,
                max_value=10,
                width="small",
            ),
            "Nome": st.column_config.TextColumn("Nome", width="medium"),
            "Resumo": st.column_config.TextColumn(
                "Resumo da Análise",
                width="large",
                help="Resumo gerado pela IA com base no currículo",
            ),
            "Cidade/Estado": st.column_config.TextColumn("Cidade/Estado", width="small"),
            "Formação": st.column_config.TextColumn("Formação", width="medium"),
            "Experiência": st.column_config.TextColumn("Experiência", width="large"),
            "Habilidades": st.column_config.TextColumn("Habilidades", width="large"),
            "Idiomas": st.column_config.TextColumn("Idiomas", width="small"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
            "Telefone": st.column_config.TextColumn("Telefone", width="small"),
            "Justificativa": st.column_config.TextColumn("Justificativa da Nota", width="large"),
            "Data de Análise": st.column_config.TextColumn("Data", width="small"),
            "Arquivo": st.column_config.TextColumn("Arquivo", width="medium"),
        },
        hide_index=True,
    )

    st.caption(f"{len(df_view)} candidato(s) exibido(s). Clique em uma célula para ver o texto completo.")

# ═══════════════════════════════════════════════════════════════════════════════
# ABA 3 — Ranking / gráfico
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ranking:
    st.markdown("#### Ranking de candidatos por nota")

    chart_df = df.copy()
    chart_df["Nota"] = pd.to_numeric(chart_df["Nota"], errors="coerce")
    chart_df = chart_df.dropna(subset=["Nota"]).sort_values("Nota", ascending=True)
    chart_df["Nome"] = chart_df["Nome"].fillna(chart_df["Arquivo"])

    fig = px.bar(
        chart_df, x="Nota", y="Nome", orientation="h",
        color="Nota", color_continuous_scale=["#FCA5A5", "#FCD34D", "#34D399"],
        range_color=[0, 10],
        labels={"Nota": "Nota (0–10)", "Nome": ""},
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color="#1E3A8A", coloraxis_showscale=False,
        margin=dict(l=0, r=20, t=10, b=20),
        height=max(300, len(chart_df) * 38),
    )
    fig.add_vline(x=7, line_dash="dot", line_color="#2563EB", annotation_text="Meta 7")
    st.plotly_chart(fig, use_container_width=True)
