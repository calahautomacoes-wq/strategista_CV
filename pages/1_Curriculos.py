import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Currículos · StrategisTA", page_icon="📄", layout="wide")

st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .stApp { background: #EFF6FF; }

  .page-title {
    font-size: 1.8rem; font-weight: 800; color: #1E3A8A;
    margin-bottom: 0.2rem;
  }
  .page-sub { color: #64748B; margin-bottom: 1.5rem; }

  .cv-card {
    background: white; border-radius: 16px; padding: 1.5rem 1.8rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.09); border: 1px solid #DBEAFE;
    margin-bottom: 1rem;
  }
  .cv-name { font-size: 1.3rem; font-weight: 700; color: #1E3A8A; }
  .cv-meta { font-size: 0.82rem; color: #64748B; margin: 4px 0 12px; }
  .cv-section { font-size: 0.75rem; font-weight: 700; color: #2563EB;
                text-transform: uppercase; letter-spacing: 1px; margin-top: 12px; }
  .cv-text { font-size: 0.88rem; color: #334155; margin-top: 4px; }
  .nota-badge {
    display: inline-block; background: #EFF6FF; border: 2px solid #2563EB;
    color: #1E40AF; font-weight: 800; font-size: 1.5rem;
    border-radius: 50%; width: 52px; height: 52px; line-height: 48px;
    text-align: center; float: right;
  }

  div[data-testid="stTextInput"] input { border-radius: 10px; border: 1px solid #DBEAFE; }
  div[data-testid="stSelectbox"] { border-radius: 10px; }

  thead tr th {
    background: #EFF6FF !important; color: #1E3A8A !important;
    font-weight: 700 !important; font-size: 0.8rem !important;
  }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="page-title">📄 Currículos Analisados</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Visualize, filtre e explore os currículos registrados na planilha.</p>', unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load():
    try:
        from utils.sheets import get_all_cvs
        return get_all_cvs()
    except FileNotFoundError:
        return None
    except Exception as exc:
        st.error(f"Erro ao carregar planilha: {exc}")
        return pd.DataFrame()

df = load()

if df is None:
    st.warning("**credentials.json** não encontrado. Configure o Google Sheets na página inicial antes de continuar.")
    st.stop()

if df.empty:
    st.info("Nenhum currículo analisado ainda. Vá à página inicial e clique em **Buscar CV**.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    search = st.text_input("🔍 Buscar por nome, habilidade ou cidade", placeholder="Ex: Python, São Paulo...")
with f2:
    nota_min = st.slider("Nota mínima", 1, 10, 1)
with f3:
    ordenar = st.selectbox("Ordenar por", ["Nota ↓", "Nota ↑", "Nome A-Z", "Mais recente"])

filtered = df.copy()
if search:
    mask = filtered.apply(lambda row: search.lower() in row.to_string().lower(), axis=1)
    filtered = filtered[mask]

filtered = filtered[filtered["Nota"] >= nota_min]

sort_map = {
    "Nota ↓": ("Nota", False),
    "Nota ↑": ("Nota", True),
    "Nome A-Z": ("Nome", True),
    "Mais recente": ("Data de Análise", False),
}
col, asc = sort_map[ordenar]
filtered = filtered.sort_values(col, ascending=asc).reset_index(drop=True)

# ── Summary chart + table toggle ──────────────────────────────────────────────
tab_cards, tab_table, tab_chart = st.tabs(["Cards", "Tabela", "Gráfico"])

with tab_cards:
    if filtered.empty:
        st.info("Nenhum currículo corresponde aos filtros.")
    else:
        st.caption(f"{len(filtered)} currículo(s) encontrado(s)")
        for _, row in filtered.iterrows():
            nota_val = row.get("Nota", "")
            nota_str = f"{nota_val:.0f}" if pd.notna(nota_val) and nota_val != "" else "—"
            st.markdown(f"""
            <div class="cv-card">
              <span class="nota-badge">{nota_str}</span>
              <div class="cv-name">{row.get('Nome') or '—'}</div>
              <div class="cv-meta">
                📧 {row.get('Email') or '—'} &nbsp;|&nbsp;
                📱 {row.get('Telefone') or '—'} &nbsp;|&nbsp;
                📍 {row.get('Cidade/Estado') or '—'} &nbsp;|&nbsp;
                🗓 {row.get('Data de Análise') or '—'}
              </div>
              <div class="cv-section">Resumo</div>
              <div class="cv-text">{row.get('Resumo') or '—'}</div>
              <div class="cv-section">Formação</div>
              <div class="cv-text">{row.get('Formação') or '—'}</div>
              <div class="cv-section">Habilidades</div>
              <div class="cv-text">{row.get('Habilidades') or '—'}</div>
              <div class="cv-section">Justificativa da nota</div>
              <div class="cv-text">{row.get('Justificativa') or '—'}</div>
            </div>
            """, unsafe_allow_html=True)

with tab_table:
    cols_show = ["Nome", "Email", "Cidade/Estado", "Formação", "Nota", "Data de Análise"]
    st.dataframe(
        filtered[cols_show].rename(columns={"Data de Análise": "Análise"}),
        use_container_width=True,
        hide_index=True,
    )

with tab_chart:
    if filtered["Nota"].notna().any():
        fig = px.bar(
            filtered.sort_values("Nota", ascending=True),
            x="Nota", y="Nome", orientation="h",
            color="Nota", color_continuous_scale=["#BFDBFE", "#1E40AF"],
            title="Ranking por Nota",
            labels={"Nota": "Nota (1–10)", "Nome": ""},
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_color="#1E3A8A", showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de nota para exibir.")
