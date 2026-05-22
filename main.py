import streamlit as st

st.set_page_config(
    page_title="StrategisTA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("StrategisTA")
st.markdown("Welcome to the dashboard. Use the sidebar to navigate.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Metric A", value="—")
with col2:
    st.metric(label="Metric B", value="—")
with col3:
    st.metric(label="Metric C", value="—")

st.info("Add your first page under `pages/` to get started.")
