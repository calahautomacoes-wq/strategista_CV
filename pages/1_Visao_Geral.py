import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Visão Geral", layout="wide")

st.title("Visão Geral")
st.caption("Resumo dos principais indicadores")

# Placeholder chart
df = pd.DataFrame({"Mês": ["Jan", "Fev", "Mar", "Abr", "Mai"], "Valor": [10, 25, 18, 40, 35]})
fig = px.line(df, x="Mês", y="Valor", markers=True, title="Evolução mensal")
st.plotly_chart(fig, use_container_width=True)
