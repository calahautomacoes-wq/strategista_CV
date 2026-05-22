import streamlit as st


def metric_row(metrics: list[dict]):
    """Render a row of st.metric cards.

    Each dict should have keys: label, value, and optionally delta.
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
            )
